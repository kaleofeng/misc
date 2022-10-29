// ==UserScript==
// @name         微博超话批量签到
// @namespace    https://github.com/kaleofeng
// @version      1.0.0
// @description  微博超话批量签到
// @author       KaleoFeng
// @match        https://weibo.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        none
// @require      https://cdn.jsdelivr.net/npm/axios@0.27.2/dist/axios.min.js
// ==/UserScript==

//【超话列表】
//  hid 超话ID
//  hname 超话名称
let chaohuas = [{
        "hid": "100808db06c78d1e24cf708a14ce81c9b617ec",
        "hname": "测试超话"
    },
    {
        "hid": "1008084b97c8f5ab54d661a331566ab64bf9d6",
        "hname": "趣味测试超话"
    }
];

// 当前时间戳
const timestamp = new Date().getTime();

function sleep(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function doSignIn(hid, hname) {
    const url = 'https://weibo.com/p/aj/general/button?ajwvr=6';

    const rsp = await axios({
        url: url,
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://weibo.com',
            'Referer': `https://weibo.com/p/${hid}/super_index`
        },

        params: {
            'api': 'http://i.huati.weibo.com/aj/super/checkin',
            'texta': '签到',
            'textb': '已签到',
            'status': '0',
            'id': hid,
            'location': 'page_100808_super_index',
            'timezone': 'GMT 0800',
            'lang': 'zh-cn',
            'plat': 'Win32',
            'ua': 'Mozilla/5.0 (Windows%20NT%2010.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'screen': '1920*1080',
            '__rnd': timestamp,
        }
    });

    if (rsp.status != 200) {
        return {
            success: false,
            msg: `超话签到[${hname}]: ${rsp.status}-操作失败`
        };
    }

    return {
        success: rsp.data.code == '100000' || rsp.data.code == '382004',
        msg: `超话签到[${hname}]: ${rsp.data.code}-${rsp.data.msg}`
    };
}

async function run() {
    let infos = '';

    // 执行超话批量签到
    let total = chaohuas.length;
    let count = 0;
    let breakOff = false;
    for (const chaohua of chaohuas) {
        const hid = chaohua.hid;
        const hname = chaohua.hname;

        let result = await doSignIn(hid, hname);
        let info = `超话名称(${hname}) 签到结果(${result.success}) 签到详情(${result.msg})\n`;
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

    // 批量签到按钮
    var signBtn = document.createElement("button");
    signBtn.className = "btn btn-success kf-button";
    signBtn.innerText = "批量签到";
    container.appendChild(signBtn);

    // 改变所有关联按钮可点击状态
    function changeRelatedButtonState(disabled) {
        let buttons = document.getElementsByClassName('kf-button');
        for (let button of buttons) {
            button.disabled = disabled;
        }
    }

    // 点击开始执行
    signBtn.addEventListener('click', function() {
        changeRelatedButtonState(true);
        run()
            .then(result => alert(`微博超话批量签到成功！（＾∀＾）\n${result}`))
            .catch(err => alert(`微博超话批量签到出错！（>﹏<）\n${err}`))
            .finally(() => changeRelatedButtonState(false));
    }, false);
})();