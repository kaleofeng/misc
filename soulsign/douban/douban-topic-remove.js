 // ==UserScript==
// @name              豆瓣小组删除帖子
// @namespace         https://github.com/inu1255/soulsign-chrome
// @version           1.0.0
// @author            KaleoFeng
// @loginURL          https://www.douban.com
// @expire            900e3
// @grant             cookie
// @domain            www.douban.com
// @param             topicID 帖子ID
// @param             userID 仅删目标用户评论（为空则删除全部）
// @param             commentOnly 仅删评论保留帖子（为空则删除帖子）
// ==/UserScript==

const origin = 'https://www.douban.com';
let ck = '';

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function objectToUrlEncodedParams(obj) {
  return Object.entries(obj)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
}

async function doGetTopicDetail(tid, userId) {
  const url = `https://www.douban.com/group/topic/${tid}`;
  const rsp = await axios.get(url);

  if (rsp.status != 200) {
    return {
      success: false,
      msg: `进入帖子页面: ${rsp.status}-操作失败`
    };
  }

  let cidPattern = 'data-cid="(\\d*?)" >';
  if (userId != '') {
    cidPattern = `data-author-id="${userId}"[\s\n\r]*?data-cid="(\\d*?)" >`;
  }
  const cidReg = new RegExp(cidPattern, 'g');

  const cids = [];
  while ((matches = cidReg.exec(rsp.data)) != null) {
    cids.push(matches[1]);
  }

  return {
    success: true,
    cids: cids
  };
}

async function doRemoveComment(tid, cid) {
  const url = `https://www.douban.com/group/topic/${tid}/remove_comment`;

  const rsp = await axios({
    url: url,
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest',
      'Origin': origin,
      'Referer': url
    },
    params: {
      'cid': cid
    },
    data: {
      'ck': ck,
      'cid': cid,
      'reason': 'other_reason',
      'other': '不可抗力因素',
      'submit': '确定'
    },
    transformRequest: [function (data) {
      return objectToUrlEncodedParams(data);
    }]
  });

  if (rsp.status != 200) {
    return {
      success: false,
      msg: `删除评论[${tid}-${cid}]: ${rsp.status}-操作失败`
    };
  }

  return {
    success: true,
    msg: `删除评论[${tid}-${cid}]: ${rsp.status}-操作成功`
  };
}

async function doRemoveTopic(tid) {
  const url = `https://www.douban.com/group/topic/${tid}/remove`;

  const rsp = await axios({
    url: url,
    method: 'GET',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest',
      'Origin': origin,
      'Referer': url
    },
    params: {
      'ck': ck
    }
  });

  if (rsp.status != 200) {
    return {
      success: false,
      msg: `删除帖子[${tid}]: ${rsp.status}-操作失败`
    };
  }

  return {
    success: true,
    msg: `删除帖子[${tid}]: ${rsp.status}-操作成功`
  };
}

exports.run = async function(param) {
  const tid = param.topicID ? param.topicID : '';
  const userId = param.userID ? param.userID : '';
  const commentOnly = param.commentOnly ? param.commentOnly : '';

  ck = await getCookie(origin, 'ck') || '';

  let result = await doGetTopicDetail(tid, userId);
  if (!result.success) {
    throw result.msg;
  }

  const cids = Array.from(new Set(result.cids));

  for (const cid of cids) {
    let result = await doRemoveComment(tid, cid);
    if (!result.success) {
      throw result.msg;
    }

    await sleep(3000);
  }

  if (commentOnly == '' || commentOnly == '0') {
    let result = await doRemoveTopic(tid);
    return result;
    if (!result.success) {
      throw result.msg;
    }
  }

  return `操作成功: 目标帖子[${tid}-${userId}-${commentOnly}]`;
};

exports.check = async function(param) {
  return true;
};
