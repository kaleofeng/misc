// ==UserScript==
// @name         京东统计全部订单
// @namespace    https://github.com/kaleofeng
// @version      1.0.0
// @description  京东统计全部订单
// @author       KaleoFeng
// @match        https://order.jd.com/*
// @connect      www.jd.com
// @connect      details.jd.com
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        GM_xmlhttpRequest
// @require      https://cdn.jsdelivr.net/npm/axios@0.27.2/dist/axios.min.js
// ==/UserScript==

// 所有商品列表
const globalProductList = [];

function objectToUrlEncodedParams(obj) {
    return Object.entries(obj)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

function sleep(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function xmlHttpRequest(url, method, headers = {}, data = {}) {
    return new Promise((resolve, reject) => {
        GM_xmlhttpRequest({
            url: url,
            method: method,
            headers: headers,
            data: data,
            onload: function(rsp) {
                resolve({
                    status: rsp.status,
                    data: rsp.response,
                });
            },
            onerror: function(rsp) {
                reject({
                    status: rsp.status,
                    data: rsp.response,
                });
            },
        })
    });
}

function xmlHttpGet(req) {
    let url = req.url || '';
    let method = 'GET';
    let headers = req.headers || {};
    return xmlHttpRequest(url, method, headers);
}

function showInNewTab(title, data) {
    const html = `\`<title>${title}</title><div>${data}</div>\``;
    const tab = window.open('about:blank');
    tab.document.write(html);
    tab.focus();
    //chrome.tabs.create({url:`javascript:document.write(${html});`});
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
    let matches = null;
    while ((matches = regExp.exec(data)) != null) {
        dataList.push(matches[1]);
    }
    return dataList;
}

function getRegExpDataListCustom(data, regExp, dataFunc) {
    const dataList = [];
    let matches = null;
    while ((matches = regExp.exec(data)) != null) {
        dataFunc(matches, dataList)
    }
    return dataList;
}

async function fetchHtmlPageData(url) {
    const rsp = await xmlHttpGet({
        url: url,
        headers: {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'origin': 'https://order.jd.com',
            'referer': 'https://order.jd.com',
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

function createDataShowContainer(parent) {
    const mdlMain = document.createElement('div');
    mdlMain.id = 'mdl_show_data';
    mdlMain.className = 'modal fade';
    mdlMain.setAttribute('tabindex', '-1');
    parent.appendChild(mdlMain);

    const mdlDialog = document.createElement('div');
    mdlDialog.className = 'modal-dialog modal-fullscreen';
    mdlMain.appendChild(mdlDialog);

    const mdlContent = document.createElement('div');
    mdlContent.className = 'modal-content';
    mdlDialog.appendChild(mdlContent);

    const mdlHeader = document.createElement('div');
    mdlHeader.className = 'modal-header';
    mdlContent.appendChild(mdlHeader);

    const txtTitle = document.createElement('h4');
    txtTitle.id = 'txt_show_title';
    txtTitle.className = 'modal-title';
    mdlHeader.appendChild(txtTitle);

    const btnClose = document.createElement('button');
    btnClose.type = 'button';
    btnClose.className = 'btn-close';
    btnClose.setAttribute('data-bs-dismiss', 'modal');
    mdlHeader.appendChild(btnClose);

    const mdlBody = document.createElement('div');
    mdlBody.className = 'modal-body';
    mdlContent.appendChild(mdlBody);

    const txtContent = document.createElement('textarea');
    txtContent.id = 'txt_show_content';
    txtContent.className = 'w-100 h-100';
    txtContent.setAttribute('readonly', true);
    mdlBody.appendChild(txtContent);
}

function showDataInContainer(title, content) {
    const txtTitle = document.getElementById('txt_show_title');
    txtTitle.innerText = title;

    const txtContent = document.getElementById('txt_show_content');
    txtContent.innerText = content;

    let showDataModal = new bootstrap.Modal(document.getElementById('mdl_show_data'), {
        keyboard: false
    });
    showDataModal.show();
}

async function run() {
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
    showDataInContainer('订单列表', JSON.stringify(globalProductList));

    return `操作成功: 完成数量[${count}]`;
}

(function() {
    'use strict';

    // 容纳按钮的容器，同时做互斥，可能多个脚本共用
    let containerId = 'kf-container';
    let container = document.getElementById(containerId);
    if (!container) {
        // 引入Bootstrap CSS
        var bootstrapCss = document.createElement('link');
        bootstrapCss.rel = 'stylesheet';
        bootstrapCss.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css';
        document.head.appendChild(bootstrapCss);

        // 引入Bootstrap JS
        var bootstrapJs = document.createElement('script');
        bootstrapJs.type = 'text/javascript';
        bootstrapJs.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5/dist/js/bootstrap.min.js';
        document.head.appendChild(bootstrapJs);

        // 创建容器
        container = document.createElement('div');
        container.id = containerId;
        container.className = 'btn-group-vertical btn-group-sm position-fixed';
        container.style.left = '5px';
        container.style.top = '5px';
        container.style['z-index'] = "999999";
        document.body.appendChild(container);

        // 关闭按钮
        const closeBtn = document.createElement("button");
        closeBtn.type = 'button';
        closeBtn.className = 'btn-close';
        closeBtn.innerText = '';
        container.appendChild(closeBtn);

        // 点击关闭容器
        closeBtn.addEventListener('click', function() {
            document.body.removeChild(container);
        });

        // 数据展示组件
        createDataShowContainer(document.body);
    }

    // 统计全部订单按钮
    let statBtn = document.createElement("button");
    statBtn.className = "kf-button btn btn-info";
    statBtn.innerText = "统计全部订单";
    container.appendChild(statBtn);

    // 改变所有关联按钮可点击状态
    function changeRelatedButtonState(disabled) {
        let buttons = document.getElementsByClassName('kf-button');
        for (let button of buttons) {
            button.disabled = disabled;
        }
    }

    // 点击开始执行
    statBtn.addEventListener('click', function() {
        changeRelatedButtonState(true);
        run()
            .then(result => alert(`统计全部订单成功！（＾∀＾）\n${result}`))
            .catch(err => alert(`统计全部订单出错！（>﹏<）\n${err}`))
            .finally(() => changeRelatedButtonState(false));
    }, false);
})();