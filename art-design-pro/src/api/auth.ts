import request from '@/utils/http'

/**
 * 注册
 * @param data 注册参数
 * @returns 注册响应
 */
export function fetchRegister(data: Api.Auth.RegisterParams) {
  return request.post<Api.Auth.RegisterResponse>({
    url: '/api/register/',
    data
  })
}

export function fetchRegisterSmsCode(data: Api.Auth.SendSmsCodeParams) {
  return request.post<{ code: number; msg: string }>({
    url: '/api/register/sms/send/',
    data
  })
}

/**
 * 登录
 * @param params 登录参数
 * @returns 登录响应
 */
export function fetchLogin(data: Api.Auth.LoginParams) {
  return request.post<Api.Auth.LoginResponse>({
    url: '/api/login/',
    data, // ⬅️ 改为 data，将参数放在请求体中发送
    // showSuccessMessage: true 
  })
}



/**
 * 获取用户信息
 * @returns 用户信息
 */
export function fetchGetUserInfo() {
  return request.get<Api.Auth.UserInfo>({
    url: '/api/user/info/'
    // 自定义请求头
    // headers: {
    //   'X-Custom-Header': 'your-custom-value'
    // }
  })
}

export function fetchUploadUserAvatar(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post<{ url: string }>({
    url: '/api/user/avatar/upload/',
    data: formData
  })
}


