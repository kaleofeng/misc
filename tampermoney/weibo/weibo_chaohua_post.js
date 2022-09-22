// ==UserScript==
// @name         微博超话批量发帖
// @namespace    https://github.com/kaleofeng
// @version      1.0.0
// @description  微博超话批量发帖
// @author       KaleoFeng
// @match        https://weibo.com
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        none
// @require      https://cdn.jsdelivr.net/npm/axios@0.27.2/dist/axios.min.js
// ==/UserScript==

// 【超话列表】
//   hid 超话ID
//   hname 超话名称
//   text 帖子内容
//   picture 帖子附图
let chaohuas = [{
        "hid": "100808db06c78d1e24cf708a14ce81c9b617ec",
        "hname": "测试超话",
        "text": "#测试[超话]# 这是要发布的内容\r\n单图",
        "picture": "0072KUQXly1ghh1d0daf7j30jg163t9r"
    },
    {
        "hid": "1008084b97c8f5ab54d661a331566ab64bf9d6",
        "hname": "趣味测试超话",
        "text": "#测试[超话]# 这是要发布的内容\r\n多图",
        "picture": "0072KUQXly1ghh1d0daf7j30jg163t9r|0072KUQXly1ghh1d0wgjuj30j60n9ab0"
    }
];

// 当前时间戳
const timestamp = new Date().getTime();

// 用户ID
let sid = '0';

function objectToUrlEncodedParams(obj) {
    return Object.entries(obj)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
}

function sleep(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function fetchData() {
    const url = `https://cms.metazion.fun/weibo-chaohua-posts`;
    const rsp = await axios.get(url);

    if (rsp.status != 200) {
        return {
            success: false,
            msg: `拉取数据: ${rsp.status}-操作失败`
        };
    }

    chaohuas = rsp.data;

    return {
        success: true,
        msg: `拉取数据: 操作成功`,
    };
}

async function goHome() {
    const url = `https://weibo.com`;
    const rsp = await axios.get(
        url, {
            headers: {
                accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            }
        });

    if (rsp.status != 200) {
        return {
            success: false,
            msg: `进入主页: ${rsp.status}-操作失败`
        };
    }

    const jstring = JSON.stringify(rsp.data);

    const result = /\\"uid\\":(\d*?),/.exec(jstring);
    if (result == null || result.length < 2) {
        return {
            success: false,
            msg: `用户ID: 获取失败`
        };
    }

    sid = result[1];
    return {
        success: true,
        msg: `用户ID: ${sid}`
    };
}

async function doPost(hid, hname, text, picture) {
    const url = `https://weibo.com/p/aj/proxy?ajwvr=6&__rnd=${timestamp}`;

    const rsp = await axios({
        url: url,
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://weibo.com',
            'Referer': `https://weibo.com/p/${hid}/super_index`
        },
        data: {
            'id': hid,
            'domain': '100808',
            'module': 'share_topic',
            'title': '%E5%8F%91%E5%B8%96',
            'content': '',
            'api_url': 'http://i.huati.weibo.com/pcpage/super/publisher',
            'spr': '',
            'extraurl': '',
            'is_stock': '',
            'check_url': `http%3A%2F%2Fi.huati.weibo.com%2Faj%2Fsuperpublishauth%26pageid%3D${hid}%26uid%3D1764819037`,
            'location': 'page_100808_super_index',
            'text': text,
            'appkey': '',
            'style_type': 1,
            'pic_id': picture,
            'tid': '',
            'pdetail': hid,
            'mid': '',
            'isReEdit': 'false',
            'sync_wb': 0,
            'pub_source': 'page_2',
            'api': `http://i.huati.weibo.com/pcpage/operation/publisher/sendcontent?sign=super&page_id=${hid}`,
            'longtext': 1,
            'topic_id': `1022:${hid}`,
            'pub_type': 'dialog',
            '_t': 0
        },
        transformRequest: [function(data) {
            return objectToUrlEncodedParams(data);
        }]
    });

    if (rsp.status != 200) {
        return {
            success: false,
            msg: `超话发帖[${hname}]: ${rsp.status}-操作失败`
        };
    }

    return {
        success: rsp.data.code == '100000',
        msg: `超话发帖[${hname}]: ${rsp.data.code}-${rsp.data.msg}`
    };
}

async function run() {
    let infos = '';

    // 进入用户主页
    let result = await goHome();
    if (!result.success) {
        throw result.msg;
    }

    // 执行超话批量关注
    let total = chaohuas.length;
    let count = 0;
    let breakOff = false;
    for (const chaohua of chaohuas) {
        const hid = chaohua.hid;
        const hname = chaohua.hname;
        const text = chaohua.text.replace(/\\r\\n/g, '\r\n');
        const picture = chaohua.picture;

        let result = await doPost(hid, hname, text, picture);
        let info = `超话名称(${hname}) 发帖结果(${result.success}) 发帖详情(${result.msg})\n`;
        console.log(info);
        infos += info;

        if (!result.success) {
            breakOff = true;
            break;
        }

        ++count;
        await sleep(3000);
    }

    infos += `完成数量[${count}/${total}]`;

    if (breakOff) {
        throw infos;
    }
    return infos;
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

        // 创建容器
        container = document.createElement('div');
        container.id = containerId;
        container.className = 'btn-group-vertical btn-group-sm position-fixed';
        container.style.left = '5px';
        container.style.top = '5px';
        container.style['z-index'] = "999999";
        document.body.appendChild(container);

        // 关闭按钮
        let closeBtn = document.createElement("button");
        closeBtn.className = 'btn-close';
        closeBtn.innerText = '';
        container.appendChild(closeBtn);

        // 点击关闭容器
        closeBtn.addEventListener('click', function() {
            document.body.removeChild(container);
        });
    }

    // 批量发帖按钮
    var postBtn = document.createElement("button");
    postBtn.className = "btn btn-primary kf-button";
    postBtn.innerText = "批量发帖";
    container.appendChild(postBtn);

    // 改变所有关联按钮可点击状态
    function changeRelatedButtonState(disabled) {
        let buttons = document.getElementsByClassName('kf-button');
        for (let button of buttons) {
            button.disabled = disabled;
        }
    }

    // 点击开始执行
    postBtn.addEventListener('click', function() {
        changeRelatedButtonState(true);
        run()
            .then(result => alert(`微博超话批量发帖成功！（＾∀＾）\n${result}`))
            .catch(err => alert(`微博超话批量发帖出错！（>﹏<）\n${err}`))
            .finally(() => changeRelatedButtonState(false));
    }, false);
})();