 // ==UserScript==
// @name              微博超话批量签到
// @namespace         https://github.com/inu1255/soulsign-chrome
// @version           1.0.0
// @author            KaleoFeng
// @loginURL          https://weibo.com
// @expire            900e3
// @domain            weibo.com
// @domain            cms.metazion.fun
// @param             reserved 暂无参数
// ==/UserScript==

// 【本地超话列表】
// hid 超话ID
// hname 超话名称
let chaohuas = [
  {
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

async function fetchData() {
  const url = `https://cms.metazion.fun/weibo-chaohua-infos`;
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

exports.run = async function(param) {
  let result = {};

  // 从云端拉取超话列表，如使用本地数据，请在上面配置【本地超话列表】并注释掉下面4行
  result = await fetchData();
  if (!result.success) {
    throw result.msg;
  }

  // 执行超话批量签到
  let count = 0;
  for (const chaohua of chaohuas) {
    const hid = chaohua['hid'];
    const hname = chaohua['hname'];

    let result = await doSignIn(hid, hname);
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
