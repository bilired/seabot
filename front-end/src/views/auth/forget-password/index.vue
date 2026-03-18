<!-- Forgot password page -->
<template>
  <div class="flex w-full h-screen">
    <LoginLeftView />

    <div class="relative flex-1">
      <AuthTopBar />

      <div class="auth-right-wrap">
        <div class="form">
          <h3 class="title">{{ $t('forgetPassword.title') }}</h3>
          <p class="sub-title">{{ $t('forgetPassword.subTitle') }}</p>

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
                :placeholder="$t('forgetPassword.placeholder.username')"
              />
            </ElFormItem>

            <ElFormItem prop="mobile">
              <ElInput
                class="custom-height"
                v-model.trim="formData.mobile"
                :placeholder="$t('forgetPassword.placeholder.mobile')"
              />
            </ElFormItem>

            <ElFormItem prop="smsCode">
              <div class="flex w-full gap-2">
                <ElInput
                  class="custom-height"
                  v-model.trim="formData.smsCode"
                  :placeholder="$t('forgetPassword.placeholder.smsCode')"
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
                :placeholder="$t('forgetPassword.placeholder.newPassword')"
                type="password"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <ElFormItem prop="confirmPassword">
              <ElInput
                class="custom-height"
                v-model.trim="formData.confirmPassword"
                :placeholder="$t('forgetPassword.placeholder.confirmPassword')"
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
                {{ $t('forgetPassword.submitBtnText') }}
              </ElButton>
            </div>

            <div class="mt-5 text-sm text-g-600">
              <span>{{ $t('forgetPassword.rememberedPassword') }}</span>
              <RouterLink class="text-theme" :to="{ name: 'Login' }">{{
                $t('forgetPassword.backBtnText')
              }}</RouterLink>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeUnmount, reactive, ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import type { FormInstance, FormRules } from 'element-plus'
  import { fetchSendForgetPasswordSmsCode, fetchResetPassword } from '@/api/auth'
  import { HttpError } from '@/utils/http/error'

  defineOptions({ name: 'ForgetPassword' })

  const router = useRouter()
  const { t, locale } = useI18n()
  const formRef = ref<FormInstance>()
  const loading = ref(false)
  const sendCodeLoading = ref(false)
  const countDown = ref(0)
  const countDownTimer = ref<number | null>(null)
  const formKey = ref(0)

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
    return t('forgetPassword.sendCode')
  })

  watch(locale, () => {
    formKey.value++
  })

  const validateConfirmPassword = (_rule: any, value: string, callback: (e?: Error) => void) => {
    if (!value) {
      callback(new Error(t('forgetPassword.validation.confirmPasswordRequired')))
      return
    }
    if (value !== formData.newPassword) {
      callback(new Error(t('forgetPassword.validation.passwordMismatch')))
      return
    }
    callback()
  }

  const rules = computed<FormRules<ForgetPasswordForm>>(() => ({
    username: [{ required: true, message: t('forgetPassword.validation.usernameRequired'), trigger: 'blur' }],
    mobile: [
      { required: true, message: t('forgetPassword.validation.mobileRequired'), trigger: 'blur' },
      { pattern: MOBILE_REGEXP, message: t('forgetPassword.validation.mobileInvalid'), trigger: 'blur' }
    ],
    smsCode: [{ required: true, message: t('forgetPassword.validation.smsCodeRequired'), trigger: 'blur' }],
    newPassword: [
      { required: true, message: t('forgetPassword.validation.newPasswordRequired'), trigger: 'blur' },
      { min: 6, message: t('forgetPassword.validation.newPasswordMin'), trigger: 'blur' }
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
      ElMessage.warning(t('forgetPassword.messages.fillUsernameFirst'))
      return
    }
    if (!MOBILE_REGEXP.test(formData.mobile)) {
      ElMessage.warning(t('forgetPassword.messages.fillValidMobileFirst'))
      return
    }
    sendCodeLoading.value = true
    try {
      await fetchSendForgetPasswordSmsCode({
        username: formData.username,
        mobile: formData.mobile
      })
      ElMessage.success(t('forgetPassword.messages.smsSent'))
      startCountDown()
    } catch (e) {
      if (e instanceof HttpError) {
        ElMessage.error(e.message)
      } else {
        ElMessage.error(t('forgetPassword.messages.smsFailed'))
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
      ElMessage.success(t('forgetPassword.messages.resetSuccess'))
      router.push({ name: 'Login' })
    } catch (e) {
      if (e instanceof HttpError) {
        ElMessage.error(e.message)
      } else {
        ElMessage.error(t('forgetPassword.messages.resetFailed'))
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
