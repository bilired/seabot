<!-- 忘记密码页面 -->
<template>
  <div class="flex w-full h-screen">
    <LoginLeftView />

    <div class="relative flex-1">
      <AuthTopBar />

      <div class="auth-right-wrap">
        <div class="form">
          <h3 class="title">忘记密码</h3>
          <p class="sub-title">填写账号信息，通过手机验证码重置密码</p>

          <ElForm
            class="mt-7.5"
            ref="formRef"
            :model="formData"
            :rules="rules"
            label-position="top"
          >
            <ElFormItem prop="username">
              <ElInput
                class="custom-height"
                v-model.trim="formData.username"
                placeholder="请输入用户名"
              />
            </ElFormItem>

            <ElFormItem prop="mobile">
              <ElInput
                class="custom-height"
                v-model.trim="formData.mobile"
                placeholder="请输入绑定的手机号"
              />
            </ElFormItem>

            <ElFormItem prop="smsCode">
              <div class="flex w-full gap-2">
                <ElInput
                  class="custom-height"
                  v-model.trim="formData.smsCode"
                  placeholder="请输入短信验证码"
                />
                <ElButton
                  class="custom-height"
                  :loading="sendCodeLoading"
                  :disabled="sendCodeLoading || countDown > 0"
                  @click="sendSmsCode"
                >
                  {{ sendCodeButtonText }}
                </ElButton>
              </div>
            </ElFormItem>

            <ElFormItem prop="newPassword">
              <ElInput
                class="custom-height"
                v-model.trim="formData.newPassword"
                placeholder="请输入新密码（至少6位）"
                type="password"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <ElFormItem prop="confirmPassword">
              <ElInput
                class="custom-height"
                v-model.trim="formData.confirmPassword"
                placeholder="请再次输入新密码"
                type="password"
                autocomplete="off"
                show-password
                @keyup.enter="submit"
              />
            </ElFormItem>

            <div style="margin-top: 15px">
              <ElButton
                class="w-full custom-height"
                type="primary"
                @click="submit"
                :loading="loading"
                v-ripple
              >
                确认重置
              </ElButton>
            </div>

            <div class="mt-5 text-sm text-g-600">
              <span>想起密码了？</span>
              <RouterLink class="text-theme" :to="{ name: 'Login' }">返回登录</RouterLink>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeUnmount, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'
  import { fetchSendForgetPasswordSmsCode, fetchResetPassword } from '@/api/auth'
  import { HttpError } from '@/utils/http/error'

  defineOptions({ name: 'ForgetPassword' })

  const router = useRouter()
  const formRef = ref<FormInstance>()
  const loading = ref(false)
  const sendCodeLoading = ref(false)
  const countDown = ref(0)
  const countDownTimer = ref<number | null>(null)

  const MOBILE_REGEXP = /^1\d{10}$/
  const SMS_COUNTDOWN_SECONDS = 60

  interface ForgetPasswordForm {
    username: string
    mobile: string
    smsCode: string
    newPassword: string
    confirmPassword: string
  }

  const formData = reactive<ForgetPasswordForm>({
    username: '',
    mobile: '',
    smsCode: '',
    newPassword: '',
    confirmPassword: ''
  })

  const sendCodeButtonText = computed(() => {
    if (countDown.value > 0) return `${countDown.value}s`
    return '发送验证码'
  })

  const validateConfirmPassword = (_rule: any, value: string, callback: (e?: Error) => void) => {
    if (!value) {
      callback(new Error('请再次输入新密码'))
      return
    }
    if (value !== formData.newPassword) {
      callback(new Error('两次密码输入不一致'))
      return
    }
    callback()
  }

  const rules = computed<FormRules<ForgetPasswordForm>>(() => ({
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    mobile: [
      { required: true, message: '请输入手机号', trigger: 'blur' },
      { pattern: MOBILE_REGEXP, message: '手机号格式不正确', trigger: 'blur' }
    ],
    smsCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
    newPassword: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
    ],
    confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }]
  }))

  const startCountDown = () => {
    countDown.value = SMS_COUNTDOWN_SECONDS
    countDownTimer.value = window.setInterval(() => {
      countDown.value--
      if (countDown.value <= 0) {
        clearInterval(countDownTimer.value!)
        countDownTimer.value = null
      }
    }, 1000)
  }

  const sendSmsCode = async () => {
    if (!formData.username) {
      ElMessage.warning('请先填写用户名')
      return
    }
    if (!MOBILE_REGEXP.test(formData.mobile)) {
      ElMessage.warning('请先填写正确的手机号')
      return
    }
    sendCodeLoading.value = true
    try {
      await fetchSendForgetPasswordSmsCode({
        username: formData.username,
        mobile: formData.mobile
      })
      ElMessage.success('验证码发送成功')
      startCountDown()
    } catch (e) {
      if (e instanceof HttpError) {
        ElMessage.error(e.message)
      } else {
        ElMessage.error('验证码发送失败')
      }
    } finally {
      sendCodeLoading.value = false
    }
  }

  const submit = async () => {
    const valid = await formRef.value?.validate().catch(() => false)
    if (!valid) return

    loading.value = true
    try {
      await fetchResetPassword({
        username: formData.username,
        mobile: formData.mobile,
        smsCode: formData.smsCode,
        newPassword: formData.newPassword,
        confirmPassword: formData.confirmPassword
      })
      ElMessage.success('密码重置成功')
      router.push({ name: 'Login' })
    } catch (e) {
      if (e instanceof HttpError) {
        ElMessage.error(e.message)
      } else {
        ElMessage.error('密码重置失败')
      }
    } finally {
      loading.value = false
    }
  }

  onBeforeUnmount(() => {
    if (countDownTimer.value) clearInterval(countDownTimer.value)
  })
</script>

<style scoped>
  @import '../login/style.css';
</style>
