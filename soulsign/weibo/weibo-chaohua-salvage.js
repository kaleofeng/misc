 // ==UserScript==
// @name              微博超话批量捞帖
// @namespace         https://github.com/inu1255/soulsign-chrome
// @version           1.0.0
// @author            KaleoFeng
// @loginURL          https://weibo.com
// @expire            900e3
// @domain            weibo.com
// @domain            m.weibo.cn
// @domain            cms.metazion.fun
// @param             reserved 暂无参数
// ==/UserScript==

// 【本地超话列表】
// hid 超话ID
// hname 超话名称
// text 帖子内容
// number 捞帖数量
// commentThreshold 帖子评论数量阈值 若帖子评论数已达到该数量则不评论，配置为-1则无该规则
let chaohuas = [
  {
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

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function objectToUrlEncodedParams(obj) {
  return Object.entries(obj)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
}

async function fetchData() {
  const url = `https://cms.metazion.fun/weibo-chaohua-salvages`;
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
    url,
    {
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
    success: rsp.data.code == '100000' || rsp.data.code == '100001',
    msg: `超话回帖[${hname}]: ${rsp.data.code}-${rsp.data.msg}`
  };
}

async function doSalvage(hid, hname, text, number, commentThreshold) {
  const url = 'https://m.weibo.cn/api/container/getIndex';

  let sinceId = 0;
  const midList = [];

  while (midList.length < number) {
    const rsp = await axios({
      url: url,
      method: 'GET',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://m.weibo.cn',
        'Referer': 'https://m.weibo.cn'
      },
      params: {
        'containerid': hid + '_-_sort_time',
        'luicode': '10000011',
        'lfid': hid,
        'since_id': sinceId
      }
    });

    if (rsp.status != 200) {
      return {
        success: false,
        msg: `超话捞帖: ${rsp.status}-操作失败`
      };
    }

    const jstring = JSON.stringify(rsp.data);

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
      const mid  = mids[i];
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

exports.run = async function(param) {
  let result = {};

  // 从云端拉取超话列表，如使用本地数据，请在上面配置【本地超话列表】并注释掉下面4行
  // result = await fetchData();
  // if (!result.success) {
  //   throw result.msg;
  // }

  // 进入用户主页
  result = await goHome();
  if (!result.success) {
    throw result.msg;
  }

  // 执行超话批量捞贴
  let count = 0;
  for (const chaohua of chaohuas) {
    const hid = chaohua['hid'];
    const hname = chaohua['hname'];
    const text = chaohua['text'].replace(/\\r\\n/g, '\r\n');
    const number = chaohua['number'];
    const commentThreshold = chaohua['commentThreshold'];

    let result = await doSalvage(hid, hname, text, number, commentThreshold);
    if (!result.success) {
      throw result.msg;
    }

    ++count;
    await sleep(3000);
  }

  return `操作成功: 完成数量[${count}]`;
};

exports.check = async function(param) {
  return true;
};
