/**
 * Cloudflare Pages Functions - 福彩官方接口反向代理
 * 路由: /api/ssq
 * 解决浏览器端直接请求 cwl.gov.cn 出现的跨域 (CORS) 和 Mixed Content (HTTPS -> HTTP) 限制
 */

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  
  // 处理 OPTIONS 预检请求
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
  const issueCount = url.searchParams.get("issueCount") || "";

  // 拼接中国福彩官方 API 地址
  const targetUrl = `http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=${encodeURIComponent(issueCount)}&issueStart=&issueEnd=&dayStart=&dayEnd=&pageNo=${encodeURIComponent(pageNo)}&pageSize=${encodeURIComponent(pageSize)}&week=&systemType=PC`;

  try {
    const upstreamResponse = await fetch(targetUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "http://www.cwl.gov.cn/ygfw/zq/ssq/",
        "X-Requested-With": "XMLHttpRequest"
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
        "Cache-Control": "public, max-age=300" // 缓存5分钟，避免过高频次请求官方接口
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      error: "Failed to fetch from official CWL API",
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
