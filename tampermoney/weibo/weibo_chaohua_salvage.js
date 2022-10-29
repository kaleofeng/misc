// ==UserScript==
// @name         微博超话批量捞帖
// @namespace    https://github.com/kaleofeng
// @version      1.0.0
// @description  微博超话批量捞帖
// @author       KaleoFeng
// @match        https://weibo.com/*
// @connect      m.weibo.cn
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        GM_xmlhttpRequest
// @require      https://cdn.jsdelivr.net/npm/axios@0.27.2/dist/axios.min.js
// ==/UserScript==

// 【本地超话列表】
//   hid 超话ID
//   hname 超话名称
//   text 帖子内容
//   number 捞帖数量
//   commentThreshold 帖子评论数量阈值 若帖子评论数已达到该数量则不评论，配置为-1则无该规则
let chaohuas = [{
        "hid": "100808db06c78d1e24cf708a14ce81c9b617ec",
        "hname": "测试超话",
        "text": "微博超话\r\n批量捞帖",
        "number": 3,
        "commentThreshold": -1
    },
    {
        "hid": "1008084b97c8f5ab54d661a331566ab64bf9d6",
        "hname": "趣味测试超话",
        "text": "微博超话\r\n批量捞帖",
        "number": 3,
        "commentThreshold": 25
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
    let params = req.params || {};
    return xmlHttpRequest(`${url}?${objectToUrlEncodedParams(params)}`, method, headers);
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

async function doComment(hid, hname, mid, text, forward) {
    const url = `https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=${timestamp}`;

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
            'act': 'post',
            'mid': mid,
            'uid': sid,
            'forward': forward,
            'isroot': 0,
            'content': text,
            'location': 'page_100808_super_index',
            'module': 'scommlist',
            'group_source': '',
            'filter_actionlog': '',
            'pdetail': hid,
            '_t': 0
        },
        transformRequest: [function(data) {
            return objectToUrlEncodedParams(data);
        }]
    });

    if (rsp.status != 200) {
        return {
            success: false,
            msg: `超话回帖[${hname}]: ${rsp.status}-操作失败`
        };
    }

    return {
        success: rsp.data.code == '100000' || rsp.data.code == '100001',
        msg: `超话回帖[${hname}]: ${rsp.data.code}-${rsp.data.msg}`
    };
}

async function doSalvage(hid, hname, text, number, commentThreshold) {
    const url = 'https://m.weibo.cn/api/container/getIndex';

    let sinceId = 0;
    const midList = [];

    while (midList.length < number) {
        const rsp = await xmlHttpGet({
            url: url,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://m.weibo.cn',
                'Referer': 'https://m.weibo.cn',
            },
            params: {
                'containerid': hid + '_-_sort_time',
                'luicode': '10000011',
                'lfid': hid,
                'since_id': sinceId,
            },
        });

        if (rsp.status != 200) {
            return {
                success: false,
                msg: `超话捞帖: ${rsp.status}-操作失败`
            };
        }

        const jstring = rsp.data;
        let matches = null;
        const sinceIdReg = /"since_id":(\d*?),/g;
        if ((matches = sinceIdReg.exec(jstring)) != null) {
            sinceId = matches[1];
        }

        if (sinceId == 0) {
            break;
        }

        const midReg = /"mid":"(.*?)"/g;
        const mids = [];
        while ((matches = midReg.exec(jstring)) != null) {
            mids.push(matches[1]);
        }

        const commentsCountReg = /"comments_count":(\d*?),/g;
        const commentsCounts = [];
        while ((matches = commentsCountReg.exec(jstring)) != null) {
            commentsCounts.push(matches[1]);
        }

        if (mids.length != commentsCounts.length) {
            break;
        }

        for (let i = 0; i < mids.length; ++i) {
            const mid = mids[i];
            const commentsCount = commentsCounts[i];
            if (commentThreshold < 0 || commentsCount < commentThreshold) {
                midList.push(mid);
            }
            if (midList.length >= number) {
                break;
            }
        }
    }

    let count = 0;
    for (const mid of midList) {
        const result = await doComment(hid, hname, mid, text, 0);
        if (!result.success) {
            throw result.msg;
        }

        ++count;
        await sleep(3000);
    }

    return {
        success: true,
        msg: `超话捞帖: 完成数量[${count}]`
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
        const number = chaohua.number;
        const commentThreshold = chaohua.commentThreshold;

        let result = await doSalvage(hid, hname, text, number, commentThreshold);
        let info = `超话名称(${hname}) 捞帖结果(${result.success}) 捞帖详情(${result.msg})\n`;
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

    // 批量捞帖按钮
    var salvageBtn = document.createElement("button");
    salvageBtn.className = "btn btn-warning kf-button";
    salvageBtn.innerText = "批量捞帖";
    container.appendChild(salvageBtn);

    // 改变所有关联按钮可点击状态
    function changeRelatedButtonState(disabled) {
        let buttons = document.getElementsByClassName('kf-button');
        for (let button of buttons) {
            button.disabled = disabled;
        }
    }

    // 点击开始执行
    salvageBtn.addEventListener('click', function() {
        changeRelatedButtonState(true);
        run()
            .then(result => alert(`微博超话批量捞帖成功！（＾∀＾）\n${result}`))
            .catch(err => alert(`微博超话批量捞帖出错！（>﹏<）\n${err}`))
            .finally(() => changeRelatedButtonState(false));
    }, false);
})();