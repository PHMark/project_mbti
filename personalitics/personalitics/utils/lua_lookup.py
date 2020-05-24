lua_dict = dict()

lua_dict['login'] = '''function main(splash, args)
  splash:init_cookies(splash.args.cookies)
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })
  assert(splash:wait(0.5))

  local entries = splash:history()
  local last_response = entries[#entries].response
  
  init_login_xpath = "//button[contains(., 'Log In')]"
  init_login_elem = splash:evaljs('document.evaluate("' .. init_login_xpath .. '", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue')
  init_login_elem:click()
  assert(splash:wait(1))
  
  email_xpath = "//*[contains(@type, 'email')]"
  email_elem = splash:evaljs('document.evaluate("' .. email_xpath .. '", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue')
  email_elem:focus()
  email_elem:send_text("dotes.master@gmail.com")
  assert(splash:wait(0.5))
  
  passw_xpath = "//*[contains(@type, 'password')]"
  passw_elem = splash:evaljs('document.evaluate("' .. passw_xpath .. '", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue')
  passw_elem:focus()
  passw_elem:send_text("petmalulodi001")
  assert(splash:wait(1))
  
  login_xpath = "//button[contains(., 'Log In') and following-sibling::a]"
  login_elem = splash:evaljs('document.evaluate("' .. login_xpath .. '", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue')
  login_elem:click()
  assert(splash:wait(4))
  
  return {
    url = splash:url(),
    headers = last_response.headers,
    http_status = last_response.status,
    cookies = splash:get_cookies(),
    html = splash:html(),
  }
end'''


lua_dict['render_js'] = '''function main(splash, args)
  splash:init_cookies(splash.args.cookies)
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })
  assert(splash:wait(0.5))
  local entries = splash:history()
  local last_response = entries[#entries].response

  return {
    url = splash:url(),
    headers = last_response.headers,
    http_status = last_response.status,
    cookies = splash:get_cookies(),
    html = splash:html(),
  }
end'''