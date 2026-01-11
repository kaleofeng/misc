// ==UserScript==
// @name         牛津词典清爽页面
// @namespace    https://github.com/kaleofeng
// @version      1.0.0
// @description  隐藏牛津词典页面上的广告及干扰元素
// @author       KaleoFeng
// @match        *://*.oxfordlearnersdictionaries.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function () {
    'use strict';

    console.log('[牛津词典清爽] 开始执行...');

    // 1. 环境防御：如果在受限的 iframe 中则不执行任何逻辑
    if (window.self !== window.top) {
        return;
    }

    // 2. 配置需要隐藏的选择器
    const selectorsToHide = [
        '[id^="img"]:not(iframe)', // 匹配 id 以 "img" 开头的元素
        '[id^="ring"]:not(iframe)', // 匹配 id 以 "ring" 开头的元素
        '.responsive_entry_left', // 特定 class 元素
        '[class*="img"]:not(iframe)', // 匹配 class 包含 "img" 的元素
        '[class*="am-entry"]:not(iframe)', // 匹配 class 包含 "am-entry" 的元素
        '.top-g-container', // 常见的顶部广告栏
        'iframe[src*="googleads"]', // 常见的谷歌广告 iframe
        'iframe[id*="google_ads"]' // 常见的谷歌广告 iframe
    ];

    // 3. 使用 CSS 注入而非 JS 轮询
    // 这种方式性能最高，且不会触发 DOM 操作导致的 postMessage 通信冲突
    const styleContent = `
        ${selectorsToHide.join(', ')} {
            display: none !important;
        }
    `;

    // 4. 将样式注入到 HTML 头部
    const injectStyle = () => {
        const style = document.createElement('style');
        style.textContent = styleContent;
        (document.head || document.documentElement).appendChild(style);
    };

    // 执行注入
    injectStyle();

    console.log('[牛津词典清爽] CSS 策略已注入，已跳过敏感 iframe 环境。');
})();