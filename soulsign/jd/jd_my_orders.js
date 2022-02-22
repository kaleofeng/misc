// ==UserScript==
// @name          京东我的订单
// @namespace     https://github.com/inu1255/soulsign-chrome
// @version       1.0.0
// @author        KaleoFeng
// @loginURL      https://jd.com
// @expire        900e3
// @domain        *.jd.com
// @param         reserved 暂无参数
// @grant         notify
// ==/UserScript==

// 所有商品列表
const globalProductList = [];

function sleep(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function getRegExpOneData(data, regExp) {
    const matches = regExp.exec(data);
    if (matches != null) {
        return matches[1];
    }
    return '';
}

function getRegExpDataList(data, regExp) {
    const dataList = [];
    while ((matches = regExp.exec(data)) != null) {
        dataList.push(matches[1]);
    }
    return dataList;
}

function getRegExpDataListCustom(data, regExp, dataFunc) {
    const dataList = [];
    while ((matches = regExp.exec(data)) != null) {
        dataFunc(matches, dataList)
    }
    return dataList;
}

async function fetchHtmlPageData(url) {
    const rsp = await axios.get(
        url, {
        headers: {
            accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
    });

    if (rsp.status != 200) {
        return {
            success: false,
            msg: `获取订单首页: 失败-${rsp.status}`
        };
    }

    return {
        success: true,
        data: rsp.data
    };
}

async function parseOrderDetailData(url) {
    // 获取详情页面数据
    let result = await fetchHtmlPageData(url);
    if (!result.success) {
        throw result.msg;
    }

    const detailData = result.data;

    const itemList = getRegExpDataListCustom(
        detailData,
        /"p-name"[\s\S]*?item[\s\S]*?title="(.*?)"[\s\S]*?f-price[\s\S]*?([.\d]+)[\s\S]*?<td>(\d+)</g,
        (matches, dataList) => {
            dataList.push([matches[1], matches[2], matches[3]]);
        });

    if (itemList.length < 1) {
        return {
            success: false,
            msg: `获取订单详情: 失败-${url}`
        };
    }

    const detailList = [];
    for (let i = 0; i < itemList.length; i++) {
        const itemDetail = {};
        itemDetail.name = itemList[i][0];
        itemDetail.price = itemList[i][1];
        itemDetail.amount = itemList[i][2];
        detailList.push(itemDetail);
    }

    return {
        success: true,
        data: detailList
    };
}

async function parseOrderBlockData(data) {
    const productList = [];

    const orderId = getRegExpOneData(data, /_orderid="(.*?)"/g);
    const dealTime = getRegExpOneData(data, /(?<=dealtime") title="(.*?)"/g);
    const costMoney = getRegExpOneData(data, /"amount">[\s\S]*?([\d.]+?)</g);
    const itemList = getRegExpDataListCustom(
        data,
        /"p-name"[\s\S]*?title="(.*?)"[\s\S]*?goods-number">[\s\S]*?\w(\d*)/g,
        (matches, dataList) => {
            dataList.push([matches[1], matches[2]]);
        });

    if (itemList.length < 1) {
        console.log(`获取订单详情: 异常-${orderId}`);

        return {
            success: true,
            data: productList
        };
    }

    // 如果同一个订单有多个商品或商品数量超过1个，需要深入订单详情
    if (itemList.length > 1 || parseInt(itemList[0][1]) > 1) {
        const orderDetailUri = getRegExpOneData(data, /(details.+?)"/g);
        const result = await parseOrderDetailData(`https://${orderDetailUri}`)
        if (!result.success) {
            throw result.msg;
        }

        for (const itemDetail of result.data) {
            const productInfo = {};
            productInfo.orderId = orderId;
            productInfo.dealTime = dealTime;
            productInfo.costMoney = costMoney;
            productInfo.itemName = itemDetail.name;
            productInfo.itemPrice = itemDetail.price;
            productInfo.itemAmount = itemDetail.amount;
            productList.push(productInfo);
        }
    } else {
        const productInfo = {};
        productInfo.orderId = orderId;
        productInfo.dealTime = dealTime;
        productInfo.costMoney = costMoney;
        productInfo.itemName = itemList[0][0];
        productInfo.itemPrice = costMoney;
        productInfo.itemAmount = itemList[0][1];
        productList.push(productInfo);
    }


    globalProductList.push.apply(globalProductList, productList);

    return {
        success: true,
        data: productList
    };
}

async function parseOrderPageData(data) {
    // 获取订单块数据
    const blockList = getRegExpDataList(data, /(<tbody id="tb[\s\S]*?body>)/g);

    // 解析每个订单块数据
    for (const blockData of blockList) {
        const result = await parseOrderBlockData(blockData);
        if (!result.success) {
            throw result.msg;
        }
    }

    return {
        success: true,
        data: blockList
    };
}

async function fetchOrderPageData(uri) {
    const url = `https://order.jd.com/center/list.action?search=0&d=${uri}`;
    return fetchHtmlPageData(url);
}

async function statYearPageData(uri) {
    console.log(uri)

    // 获取该年页面数据
    let result = await fetchOrderPageData(uri);
    if (!result.success) {
        throw result.msg;
    }

    const pageData = result.data;

    // 解析订单块数据
    result = await parseOrderPageData(pageData);
    if (!result.success) {
        throw result.msg;
    }

    // 解析下一页
    const nextPageUri = getRegExpOneData(pageData, /d=(.*)">下一页/g);
    if (nextPageUri.length > 0) {
        result = await statYearPageData(nextPageUri);
        if (!result.success) {
            throw result.msg;
        }

        await sleep(1000);
    }

    return {
        success: true,
        data: result.data
    };
}

function parseTimeListData(data) {
    // 获取时间列表
    const timeList = getRegExpDataList(data, /_val="(.*?)"/g);

    if (timeList.length < 1) {
        return {
            success: false,
            msg: `解析时间列表: 失败`
        };
    }

    return {
        success: true,
        data: timeList
    };
}

exports.run = async function (param) {
    globalProductList.length = 0;

    // 获取初始页数据
    let result = await fetchOrderPageData('1&s=4096');
    if (!result.success) {
        throw result.msg;
    }

    const pageData = result.data;

    // 解析时间列表
    result = parseTimeListData(pageData);
    if (!result.success) {
        throw result.msg;
    }

    const timeList = result.data;

    // 统计分析每个时间数据，第1个元素为近三个月订单，包含在后续年订单里面，所以跳过
    let count = 0;
    for (let i = 1; i < timeList.length; i++) {
        let result = await statYearPageData(timeList[i]);
        if (!result.success) {
            throw result.msg;
        }

        ++count;
        await sleep(2000);
    }

    console.log(JSON.stringify(globalProductList));
    showInNewTab('订单列表', JSON.stringify(globalProductList));
    notify('执行完成，请查看浏览器新打开标签页面获取数据');

    return `操作成功: 完成数量[${count}]`;
};

exports.check = async function (param) {
    return true;
};
