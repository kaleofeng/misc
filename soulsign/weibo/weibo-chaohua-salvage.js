 // ==UserScript==
// @name              微博超话批量捞帖
// @namespace         https://github.com/inu1255/soulsign-chrome
// @version           1.0.0
// @author            KaleoFeng
// @loginURL          https://weibo.com
// @expire            900e3
// @domain            weibo.com
// @param             reserved 暂无参数
// ==/UserScript==

// 超话列表
const chaohuas = [
  {
    "hid": "100808db06c78d1e24cf708a14ce81c9b617ec",
    "hname": "测试超话",
    "text": "微博超话\r\n批量捞帖",
    "number": 3
  },
  {
    "hid": "1008084b97c8f5ab54d661a331566ab64bf9d6",
    "hname": "趣味测试超话",
    "text": "微博超话\r\n批量捞帖",
    "number": 3
  }
];

// 当前时间戳
const timestamp = new Date().getTime();

// 用户ID
let sid = '0';

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function objectToUrlEncodedParams(obj) {
  return Object.entries(obj)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
}

async function goHome() {
  const url = `https://weibo.com`;

  const rsp = await axios.get(url);

  if (rsp.status != 200) {
    return {
      success: false,
      msg: `进入主页: ${rsp.status}-操作失败`
    };
  }

  const result = /CONFIG\['uid'\]='(\d*?)'/.exec(rsp.data);
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
    transformRequest: [function (data) {
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
    success: rsp.data.code == '100000',
    msg: `超话回帖[${hname}]: ${rsp.data.code}-${rsp.data.msg}`
  };
}

async function doSalvage(hid, hname, text, number) {
  const url = `https://weibo.com/p/${hid}/super_index`;

  const rsp = await axios.get(url);

  if (rsp.status != 200) {
    return {
      success: false,
      msg: `超话捞贴: ${rsp.status}-操作失败`
    };
  }

  const reg = /mid=\\"(\d*?)\\"/g;
  const mids = [];
  while ((matches = reg.exec(rsp.data)) != null) {
    mids.push(matches[1]);
  }

  let count = 0;
  for (const mid of mids) {
    if (count >= number) {
      break;
    }

    const result = await doComment(hid, hname, mid, text, 0);
    if (!result.success) {
      throw result.msg;
    }

    ++count;
    await sleep(1000);
  }

  return {
    success: true,
    msg: `超话捞贴: 完成数量[${count}]`
  };
}

exports.run = async function(param) {
  let result = await goHome();
  if (!result.success) {
    throw result.msg;
  }

  let count = 0;
  for (const chaohua of chaohuas) {
    const hid = chaohua['hid'];
    const hname = chaohua['hname'];
    const text = chaohua['text'];
    const number = chaohua['number'];

    let result = await doSalvage(hid, hname, text, number);
    if (!result.success) {
      throw result.msg;
    }

    ++count;
    await sleep(1000);
  }

  return `操作成功: 完成数量[${count}]`;
};

exports.check = async function(param) {
  return true;
};
