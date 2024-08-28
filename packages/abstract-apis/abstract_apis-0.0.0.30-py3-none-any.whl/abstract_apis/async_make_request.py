from .request_utils import *
async def async_get_json_response(response, response_result=None, load_nested_json=True):
    response_result = response_result or 'result'
    try:
      response_json = await response.json()
    except:
      response_json = response
    if isinstance(response_json,dict):
        response_json = response_json.get(response_result, response_json)
    if load_nested_json:
        response_json = load_inner_json(response_json)
    if response_json is not None:
        return response_json
    # Fallback to the last key if 'result' is not found
    last_key = list(response_json.keys())[-1] if response_json else None
    return response_json.get(last_key, None)


async def async_get_response(response, response_result=None, raw_response=False, load_nested_json=True):
    if raw_response:
        return response
    json_response = await async_get_json_response(response, response_result=response_result, load_nested_json=load_nested_json)
    if json_response is not None:
        return json_response
    text_response = get_text_response(response)
    if text_response:
        return text_response
    return response  # Return raw content as a last resort
async def getAsyncRequest(url, data=None, headers=None,endpoint=None,status_code=False):
    async with aiohttp.ClientSession() as session:
        values = get_values_js(url=url,data=data,headers=headers,endpoint=endpoint)
        async with session.get(**values) as response:
            if status_code:
                status_code = response.status
               
                return {"result":response,"status_code":status_code}
            else:
                response = await async_get_response(response)
                return response
async def postAsyncRequest(url, data=None, headers=None,endpoint=None,status_code=False):
    async with aiohttp.ClientSession() as session:
        values = get_values_js(url=url,data=data,headers=headers,endpoint=endpoint)
        async with session.post(**values) as response:
            
            if status_code:
                status_code = response.status
                response = await async_get_response(response)
                return {"result": await async_get_response(response),"status_code":status_code}
            else:
                response = await async_get_response(response)
                return response
async def asyncMakeRequest(url, data=None, headers=None, get_post=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    response = None
    get_post = get_post.upper() or ('GET' if data == None else 'POST')
    if get_post == 'POST':
        response = await postAsyncRequest(url, data=data, headers=headers,endpoint=endpoint,status_code=status_code)
    elif get_post == 'GET':
        response = await getAsyncRequest(url, data=data, headers=headers,endpoint=endpoint,status_code=status_code)
    else:
        raise ValueError(f"Unsupported HTTP get_post: {get_post}")
    return await async_get_response(response)

async def asyncPostRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return await asyncMakeRequest(url, data=data, headers=headers, endpoint=endpoint, get_post='POST', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncGetRequest(url, data, headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    return await asyncMakeRequest(url, data=data, headers=headers, endpoint=endpoint, get_post='GET', status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncGetRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return await getRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)

async def asyncPostRpcRequest(url, method=None,params=None,jsonrpc=None,id=None,headers=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True):
    data = getRpcData(method=method,params=params,jsonrpc=jsonrpc,id=id)
    return await asyncPostRequest(url, data, headers=headers, endpoint=endpoint, status_code=status_code, raw_response=raw_response, response_result=response_result, load_nested_json=load_nested_json)
