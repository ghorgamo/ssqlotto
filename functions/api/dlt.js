/**
 * Cloudflare Pages Functions - 体彩超级大乐透官方接口反向代理
 * 路由: /api/dlt
 * 解决浏览器端直接请求体彩网数据出现的跨域 (CORS) 与 Mixed Content 限制
 */

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, User-Agent, X-Requested-With",
        "Access-Control-Max-Age": "86400"
      }
    });
  }

  const pageNo = url.searchParams.get("pageNo") || "1";
  const pageSize = url.searchParams.get("pageSize") || "50";

  // 体彩官网大乐透接口
  const targetUrl = `https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85&provinceId=0&pageSize=${encodeURIComponent(pageSize)}&isVerify=1&pageNo=${encodeURIComponent(pageNo)}`;

  try {
    const upstreamResponse = await fetch(targetUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://static.sporttery.cn/"
      }
    });

    if (!upstreamResponse.ok) {
      return new Response(JSON.stringify({
        error: `Upstream error: ${upstreamResponse.status} ${upstreamResponse.statusText}`
      }), {
        status: upstreamResponse.status,
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          "Access-Control-Allow-Origin": "*"
        }
      });
    }

    const data = await upstreamResponse.json();

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        "Content-Type": "application/json;charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300"
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      error: "Failed to fetch from official Sporttery API",
      message: error.message
    }), {
      status: 502,
      headers: {
        "Content-Type": "application/json;charset=utf-8",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
