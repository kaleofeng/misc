// ==UserScript==
// @name         朗文词典清爽页面
// @namespace    https://github.com/kaleofeng
// @version      1.0.0
// @description  朗文词典清爽页面
// @author       KaleoFeng
// @match        https://*.ldoceonline.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function () {
    'use strict';

    // 配置：需要隐藏的元素选择器列表
    const selectorsToHide = [
        '[class*="img"]', // 匹配 class 包含 "img" 的任何元素
        '[id^="img"]' // 匹配 id 以 "img" 开头的任何元素
    ];

    // 主函数：查找并隐藏所有匹配选择器的元素
    function hideElements() {
        selectorsToHide.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`[元素清理] 使用选择器 “${selector}” 找到 ${elements.length} 个元素，正在隐藏。`);

                elements.forEach(el => {
                    el.style.display = 'none';
                    // 或者使用更彻底的方式：el.remove();
                });
            }
        });
    }

    // 1. 页面加载完成后立即执行一次
    hideElements();

    // 2. 使用 MutationObserver 监听DOM变化，以处理动态加载的内容[4](@ref)
    const observer = new MutationObserver(hideElements);
    observer.observe(document.body, { childList: true, subtree: true });

    // 3. (可选) 对于某些单页应用，可以额外监听路由变化
    // window.addEventListener('popstate', hideElements);
    // window.addEventListener('pushState', hideElements);

    console.log('[元素清理] 脚本已加载并开始监控。');
})();