<template>
  <div class="change-password-page art-full-height">
    <ElCard class="art-table-card" shadow="never">
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <div class="text-lg font-medium">修改密码</div>
            <div class="text-sm text-g-500 mt-1">请按步骤完成身份校验后再设置新密码</div>
          </div>
          <ElButton @click="router.push('/user-center')">返回个人中心</ElButton>
        </div>
      </template>

      <ElSteps :active="activeStep" finish-status="success" class="mb-6">
        <ElStep title="旧密码验证" description="输入当前登录密码" />
        <ElStep title="短信验证码" description="发送并验证注册手机验证码" />
        <ElStep title="设置新密码" description="输入并确认新密码" />
      </ElSteps>

      <ElForm ref="formRef" :model="form" :rules="rules" label-width="120px" class="max-w-160">
        <ElFormItem label="旧密码" prop="oldPassword">
          <ElInput
            v-model.trim="form.oldPassword"
            type="password"
            show-password
            placeholder="请输入旧密码"
          />
        </ElFormItem>

        <ElFormItem label="手机号">
          <ElInput :model-value="maskedMobile || userMobile || '未绑定手机号'" disabled />
        </ElFormItem>

        <ElFormItem label="短信验证码" prop="smsCode">
          <div class="flex w-full gap-2">
            <ElInput
              v-model.trim="form.smsCode"
              placeholder="请输入短信验证码"
              @input="smsVerified = false"
            />
            <ElButton :loading="sendCodeLoading" :disabled="sendCodeLoading || countDown > 0" @click="sendCode">
              {{ sendCodeButtonText }}
            </ElButton>
            <ElButton type="primary" plain :loading="verifyCodeLoading" @click="verifyCode">验证验证码</ElButton>
          </div>
          <div class="mt-2 text-xs" :class="smsVerified ? 'text-green-600' : 'text-g-500'">
            {{ smsVerified ? '验证码已通过校验' : '请先发送并校验验证码' }}
          </div>
        </ElFormItem>

        <ElFormItem label="新密码" prop="newPassword">
          <ElInput
            v-model.trim="form.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </ElFormItem>

        <ElFormItem label="确认新密码" prop="confirmPassword">
          <ElInput
            v-model.trim="form.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </ElFormItem>

        <ElFormItem>
          <ElSpace>
            <ElButton type="primary" :loading="submitLoading" @click="submitChange">确认修改</ElButton>
            <ElButton @click="resetForm">重置</ElButton>
          </ElSpace>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import type { FormInstance, FormRules } from 'element-plus'
  import { ElMessage } from 'element-plus'
  import {
    fetchChangePassword,
    fetchGetUserInfo,
    fetchSendChangePasswordSmsCode,
    fetchVerifyChangePasswordSmsCode
  } from '@/api/auth'
  import { HttpError } from '@/utils/http/error'
  import { useUserStore } from '@/store/modules/user'

  defineOptions({ name: 'ChangePassword' })

  const router = useRouter()
  const userStore = useUserStore()

  const formRef = ref<FormInstance>()
  const sendCodeLoading = ref(false)
  const verifyCodeLoading = ref(false)
  const submitLoading = ref(false)
  const smsVerified = ref(false)
  const countDown = ref(0)
  const countDownTimer = ref<number | null>(null)
  const maskedMobile = ref('')

  const form = reactive({
    oldPassword: '',
    smsCode: '',
    newPassword: '',
    confirmPassword: ''
  })

  const userMobile = computed(() => (userStore.getUserInfo as { mobile?: string }).mobile || '')

  const activeStep = computed(() => {
    if (form.newPassword && form.confirmPassword) {
      return 2
    }
    if (smsVerified.value || form.smsCode) {
      return 1
    }
    return 0
  })

  const sendCodeButtonText = computed(() => {
    if (countDown.value <= 0) {
      return '获取验证码'
    }
    return `${countDown.value}s`
  })

  const rules = computed<FormRules>(() => ({
    oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
    smsCode: [{ required: true, message: '请输入短信验证码', trigger: 'blur' }],
    newPassword: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '新密码长度不能少于 6 位', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: '请确认新密码', trigger: 'blur' },
      {
        validator: (_rule, value, callback) => {
          if (!value) {
            callback(new Error('请确认新密码'))
            return
          }
          if (value !== form.newPassword) {
            callback(new Error('两次新密码输入不一致'))
            return
          }
          callback()
        },
        trigger: 'blur'
      }
    ]
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
    countDown.value = 60
    countDownTimer.value = window.setInterval(() => {
      if (countDown.value <= 1) {
        clearCountDown()
        return
      }
      countDown.value -= 1
    }, 1000)
  }

  const ensureUserMobile = async () => {
    if ((userStore.getUserInfo as { mobile?: string }).mobile) {
      return
    }
    const latest = await fetchGetUserInfo()
    userStore.setUserInfo({ ...(userStore.getUserInfo as Api.Auth.UserInfo), ...latest } as Api.Auth.UserInfo)
  }

  const sendCode = async () => {
    try {
      await ensureUserMobile()
      sendCodeLoading.value = true
      const res = await fetchSendChangePasswordSmsCode()
      maskedMobile.value = res?.mobile || ''
      smsVerified.value = false
      ElMessage.success('验证码发送成功')
      startCountDown()
    } catch (error) {
      if (!(error instanceof HttpError)) {
        console.error('发送验证码失败:', error)
      }
    } finally {
      sendCodeLoading.value = false
    }
  }

  const verifyCode = async () => {
    if (!form.smsCode) {
      ElMessage.warning('请先输入短信验证码')
      return
    }

    try {
      verifyCodeLoading.value = true
      await fetchVerifyChangePasswordSmsCode({ smsCode: form.smsCode })
      smsVerified.value = true
      ElMessage.success('验证码校验通过')
    } catch (error) {
      smsVerified.value = false
      if (!(error instanceof HttpError)) {
        console.error('验证码校验失败:', error)
      }
    } finally {
      verifyCodeLoading.value = false
    }
  }

  const submitChange = async () => {
    if (!formRef.value) {
      return
    }

    try {
      await formRef.value.validate()

      if (!smsVerified.value) {
        ElMessage.warning('请先完成短信验证码校验')
        return
      }

      submitLoading.value = true
      await fetchChangePassword({
        oldPassword: form.oldPassword,
        smsCode: form.smsCode,
        newPassword: form.newPassword,
        confirmPassword: form.confirmPassword
      })

      ElMessage.success('密码修改成功，请重新登录')
      clearCountDown()
      userStore.logOut()
    } catch (error) {
      if (!(error instanceof HttpError)) {
        console.error('修改密码失败:', error)
      }
    } finally {
      submitLoading.value = false
    }
  }

  const resetForm = () => {
    form.oldPassword = ''
    form.smsCode = ''
    form.newPassword = ''
    form.confirmPassword = ''
    smsVerified.value = false
    formRef.value?.clearValidate()
  }

  onMounted(() => {
    ensureUserMobile()
  })

  onBeforeUnmount(() => {
    clearCountDown()
  })
</script>

<style scoped></style>
