<!-- 注册页面 -->
<template>
  <div class="flex w-full h-screen">
    <LoginLeftView />

    <div class="relative flex-1">
      <AuthTopBar />

      <div class="auth-right-wrap">
        <div class="form">
          <h3 class="title">{{ $t('register.title') }}</h3>
          <p class="sub-title">{{ $t('register.subTitle') }}</p>
          <ElForm
            class="mt-7.5"
            ref="formRef"
            :model="formData"
            :rules="rules"
            label-position="top"
            :key="formKey"
          >
            <ElFormItem prop="username">
              <ElInput
                class="custom-height"
                v-model.trim="formData.username"
                :placeholder="$t('register.placeholder.username')"
              />
            </ElFormItem>

            <ElFormItem prop="mobile">
              <ElInput
                class="custom-height"
                v-model.trim="formData.mobile"
                :placeholder="$t('register.placeholder.mobile')"
              />
            </ElFormItem>

            <ElFormItem prop="smsCode">
              <div class="flex w-full gap-2">
                <ElInput
                  class="custom-height"
                  v-model.trim="formData.smsCode"
                  :placeholder="$t('register.placeholder.smsCode')"
                  @keyup.enter="register"
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

            <ElFormItem prop="password">
              <ElInput
                class="custom-height"
                v-model.trim="formData.password"
                :placeholder="$t('register.placeholder.password')"
                type="password"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <ElFormItem prop="confirmPassword">
              <ElInput
                class="custom-height"
                v-model.trim="formData.confirmPassword"
                :placeholder="$t('register.placeholder.confirmPassword')"
                type="password"
                autocomplete="off"
                @keyup.enter="register"
                show-password
              />
            </ElFormItem>

            <ElFormItem prop="agreement">
              <ElCheckbox v-model="formData.agreement">
                {{ $t('register.agreeText') }}
                <RouterLink
                  style="color: var(--theme-color); text-decoration: none"
                  to="/privacy-policy"
                  >{{ $t('register.privacyPolicy') }}</RouterLink
                >
              </ElCheckbox>
            </ElFormItem>

            <div style="margin-top: 15px">
              <ElButton
                class="w-full custom-height"
                type="primary"
                @click="register"
                :loading="loading"
                v-ripple
              >
                {{ $t('register.submitBtnText') }}
              </ElButton>
            </div>

            <div class="mt-5 text-sm text-g-600">
              <span>{{ $t('register.hasAccount') }}</span>
              <RouterLink class="text-theme" :to="{ name: 'Login' }">{{
                $t('register.toLogin')
              }}</RouterLink>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'
  import { fetchLogin, fetchRegister, fetchRegisterSmsCode } from '@/api/auth'
  import { useUserStore } from '@/store/modules/user'
  import { HttpError } from '@/utils/http/error'

  defineOptions({ name: 'Register' })

  interface RegisterForm {
    username: string
    mobile: string
    smsCode: string
    password: string
    confirmPassword: string
    agreement: boolean
  }

  const USERNAME_MIN_LENGTH = 3
  const USERNAME_MAX_LENGTH = 20
  const PASSWORD_MIN_LENGTH = 6
  const SMS_COUNTDOWN_SECONDS = 60
  const MOBILE_REGEXP = /^1\d{10}$/
  const { t, locale } = useI18n()
  const router = useRouter()
  const userStore = useUserStore()
  const formRef = ref<FormInstance>()

  const loading = ref(false)
  const sendCodeLoading = ref(false)
  const countDown = ref(0)
  const countDownTimer = ref<number | null>(null)
  const formKey = ref(0)

  // 监听语言切换，重置表单
  watch(locale, () => {
    formKey.value++
  })

  const formData = reactive<RegisterForm>({
    username: '',
    mobile: '',
    smsCode: '',
    password: '',
    confirmPassword: '',
    agreement: false
  })

  const sendCodeButtonText = computed(() => {
    if (countDown.value > 0) {
      return `${countDown.value}s`
    }
    return t('register.sendCode')
  })

  /**
   * 验证密码
   * 当密码输入后，如果确认密码已填写，则触发确认密码的验证
   */
  const validatePassword = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error(t('register.placeholder.password')))
      return
    }

    if (formData.confirmPassword) {
      formRef.value?.validateField('confirmPassword')
    }

    callback()
  }

  /**
   * 验证确认密码
   * 检查确认密码是否与密码一致
   */
  const validateConfirmPassword = (
    _rule: any,
    value: string,
    callback: (error?: Error) => void
  ) => {
    if (!value) {
      callback(new Error(t('register.rule.confirmPasswordRequired')))
      return
    }

    if (value !== formData.password) {
      callback(new Error(t('register.rule.passwordMismatch')))
      return
    }

    callback()
  }

  /**
   * 验证用户协议
   * 确保用户已勾选同意协议
   */
  const validateAgreement = (_rule: any, value: boolean, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error(t('register.rule.agreementRequired')))
      return
    }
    callback()
  }

  const validateMobile = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error(t('register.rule.mobileRequired')))
      return
    }

    if (!MOBILE_REGEXP.test(value)) {
      callback(new Error(t('register.rule.mobileInvalid')))
      return
    }

    callback()
  }

  const validateSmsCode = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error(t('register.rule.smsCodeRequired')))
      return
    }
    callback()
  }

  const rules = computed<FormRules<RegisterForm>>(() => ({
    username: [
      { required: true, message: t('register.placeholder.username'), trigger: 'blur' },
      {
        min: USERNAME_MIN_LENGTH,
        max: USERNAME_MAX_LENGTH,
        message: t('register.rule.usernameLength'),
        trigger: 'blur'
      }
    ],
    mobile: [{ required: true, validator: validateMobile, trigger: 'blur' }],
    smsCode: [{ required: true, validator: validateSmsCode, trigger: 'blur' }],
    password: [
      { required: true, validator: validatePassword, trigger: 'blur' },
      { min: PASSWORD_MIN_LENGTH, message: t('register.rule.passwordLength'), trigger: 'blur' }
    ],
    confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
    agreement: [{ validator: validateAgreement, trigger: 'change' }]
  }))

  const clearCountDown = () => {
    if (countDownTimer.value) {
      window.clearInterval(countDownTimer.value)
      countDownTimer.value = null
    }
    countDown.value = 0
  }

  const startCountDown = () => {
    clearCountDown()
    countDown.value = SMS_COUNTDOWN_SECONDS
    countDownTimer.value = window.setInterval(() => {
      if (countDown.value <= 1) {
        clearCountDown()
        return
      }
      countDown.value -= 1
    }, 1000)
  }

  const sendSmsCode = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validateField('mobile')
      sendCodeLoading.value = true

      await fetchRegisterSmsCode({
        mobile: formData.mobile
      })

      ElMessage.success(t('register.rule.smsCodeSent'))
      startCountDown()
    } catch (error) {
      if (!(error instanceof HttpError)) {
        console.error('发送验证码失败:', error)
      }
    } finally {
      sendCodeLoading.value = false
    }
  }

  /**
   * 注册用户
   * 验证表单后提交注册请求
   */
  const register = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      loading.value = true

      // 调用后端注册 API
      const registerData = await fetchRegister({
        userName: formData.username,
        mobile: formData.mobile,
        smsCode: formData.smsCode,
        password: formData.password,
        confirmPassword: formData.confirmPassword
      })

      if (registerData?.userId) {
        const loginRes = await fetchLogin({
          userName: formData.username,
          password: formData.password
        })

        userStore.setToken(loginRes.token, loginRes.refreshToken)
        userStore.setLoginStatus(true)

        ElMessage.success(t('register.successAutoLogin'))
        router.push('/')
      }
    } catch (error) {
      if (error instanceof HttpError) {
        ElMessage.error(error.message)
      } else {
        console.error('注册失败:', error)
        ElMessage.error(t('register.registerFailedRetry'))
      }
    } finally {
      loading.value = false
    }
  }

  onBeforeUnmount(() => {
    clearCountDown()
  })
</script>

<style scoped>
  @import '../login/style.css';
</style>
