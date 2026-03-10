<!-- 个人中心页面 -->
<template>
  <div class="w-full h-full p-0 bg-transparent border-none shadow-none">
    <div class="relative flex-b mt-2.5 max-md:block max-md:mt-1">
      <div class="w-112 mr-5 max-md:w-full max-md:mr-0">
        <div class="art-card-sm relative p-9 pb-6 overflow-hidden text-center">
          <img class="absolute top-0 left-0 w-full h-50 object-cover" src="@imgs/user/bg.webp" />
          <ElImage
            class="relative z-10 w-20 h-20 mt-30 mx-auto object-cover border-2 border-white rounded-full"
            :src="avatarUrl"
            :preview-src-list="[avatarUrl]"
            preview-teleported
            fit="cover"
          />
          <div class="relative z-10 mt-3">
            <ElUpload
              :show-file-list="false"
              accept="image/*"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
            >
              <ElButton size="small" :loading="avatarUploading">修改头像</ElButton>
            </ElUpload>
          </div>
          <h2 class="mt-5 text-xl font-normal">{{ form.nikeName || form.realName || userInfo.userName }}</h2>
          <p class="mt-5 text-sm">{{ form.des || '暂无个人介绍' }}</p>

          <div class="w-75 mx-auto mt-7.5 text-left">
            <div class="mt-2.5">
              <ArtSvgIcon icon="ri:mail-line" class="text-g-700" />
              <span class="ml-2 text-sm">{{ form.email || '未设置邮箱' }}</span>
            </div>
            <div class="mt-2.5">
              <ArtSvgIcon icon="ri:user-3-line" class="text-g-700" />
              <span class="ml-2 text-sm">{{ form.sex === '1' ? '男' : form.sex === '2' ? '女' : '未设置性别' }}</span>
            </div>
            <div class="mt-2.5">
              <ArtSvgIcon icon="ri:map-pin-line" class="text-g-700" />
              <span class="ml-2 text-sm">{{ form.address || '未设置地址' }}</span>
            </div>
            <div class="mt-2.5">
              <ArtSvgIcon icon="ri:phone-line" class="text-g-700" />
              <span class="ml-2 text-sm">{{ form.mobile || '未设置手机号' }}</span>
            </div>
          </div>

          <!-- <div class="mt-10">
            <h3 class="text-sm font-medium">标签</h3>
            <div class="flex flex-wrap justify-center mt-3.5">
              <div
                v-for="item in lableList"
                :key="item"
                class="py-1 px-1.5 mr-2.5 mb-2.5 text-xs border border-g-300 rounded"
              >
                {{ item }}
              </div>
            </div>
          </div> -->
        </div>
      </div>
      <div class="flex-1 overflow-hidden max-md:w-full max-md:mt-3.5">
        <div class="art-card-sm">
          <h1 class="p-4 text-xl font-normal border-b border-g-300">基本设置</h1>

          <ElForm
            :model="form"
            class="box-border p-5 [&>.el-row_.el-form-item]:w-[calc(50%-10px)] [&>.el-row_.el-input]:w-full [&>.el-row_.el-select]:w-full"
            ref="ruleFormRef"
            :rules="rules"
            label-width="86px"
            label-position="top"
          >
            <ElRow>
              <ElFormItem label="姓名" prop="realName">
                <ElInput v-model="form.realName" :disabled="!isEdit" />
              </ElFormItem>
              <ElFormItem label="性别" prop="sex" class="ml-5">
                <ElSelect v-model="form.sex" placeholder="Select" :disabled="!isEdit">
                  <ElOption
                    v-for="item in options"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </ElSelect>
              </ElFormItem>
            </ElRow>

            <ElRow>
              <ElFormItem label="昵称" prop="nikeName">
                <ElInput v-model="form.nikeName" :disabled="!isEdit" />
              </ElFormItem>
              <ElFormItem label="邮箱" prop="email" class="ml-5">
                <ElInput v-model="form.email" :disabled="!isEdit" />
              </ElFormItem>
            </ElRow>

            <ElRow>
              <ElFormItem label="手机" prop="mobile">
                <ElInput v-model="form.mobile" :disabled="!isEdit" />
              </ElFormItem>
              <ElFormItem label="地址" prop="address" class="ml-5">
                <ElInput v-model="form.address" :disabled="!isEdit" />
              </ElFormItem>
            </ElRow>

            <ElFormItem label="个人介绍" prop="des" class="h-32">
              <ElInput type="textarea" :rows="4" v-model="form.des" :disabled="!isEdit" />
            </ElFormItem>

            <div class="flex-c justify-end [&_.el-button]:!w-27.5">
              <ElButton v-if="isEdit" :disabled="saving" v-ripple @click="cancelEdit">取消</ElButton>
              <ElButton type="primary" class="w-22.5" :loading="saving" v-ripple @click="edit">
                {{ isEdit ? '保存' : '编辑' }}
              </ElButton>
            </div>
          </ElForm>
        </div>

        <div class="art-card-sm my-5">
          <h1 class="p-4 text-xl font-normal border-b border-g-300">更改密码</h1>
          <div class="box-border p-5 flex items-center justify-between max-md:block">
            <div class="text-sm text-g-600 max-md:mb-3">为保障账户安全，请在独立页面完成旧密码、短信验证码和新密码设置。</div>
            <ElButton type="primary" v-ripple @click="goChangePassword">前往修改密码</ElButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import avatarDefault from '@imgs/user/avatar.webp'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '@/store/modules/user'
  import { fetchGetUserInfo, fetchUploadUserAvatar, fetchUpdateUserProfile } from '@/api/auth'
  import { HttpError } from '@/utils/http/error'
  import type { FormInstance, FormRules, UploadRequestOptions } from 'element-plus'
  import type { UploadAjaxError } from 'element-plus/es/components/upload/src/ajax'

  defineOptions({ name: 'UserCenter' })

  const router = useRouter()
  const userStore = useUserStore()
  const userInfo = computed(() => userStore.getUserInfo)
  const avatarUploading = ref(false)
  const avatarUrl = computed(() => userInfo.value?.avatar || avatarDefault)
  const AVATAR_MAX_SIZE_MB = 5

  const isEdit = ref(false)
  const saving = ref(false)
  const ruleFormRef = ref<FormInstance>()

  /**
   * 用户信息表单
   */
  const form = reactive({
    realName: '',
    nikeName: '',
    email: '',
    mobile: '',
    address: '',
    sex: '',
    des: ''
  })

  const MOBILE_REGEXP = /^1\d{10}$/
  const EMAIL_REGEXP = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  const validateMobile = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error('请输入手机号码'))
      return
    }
    if (!MOBILE_REGEXP.test(value)) {
      callback(new Error('请输入正确的 11 位手机号'))
      return
    }
    callback()
  }

  const validateEmail = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error('请输入邮箱'))
      return
    }
    if (!EMAIL_REGEXP.test(value)) {
      callback(new Error('请输入正确的邮箱格式'))
      return
    }
    callback()
  }

  /**
   * 表单验证规则
   */
  const rules = reactive<FormRules>({
    realName: [
      { required: true, message: '请输入姓名', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    nikeName: [
      { required: true, message: '请输入昵称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    email: [{ required: true, validator: validateEmail, trigger: 'blur' }],
    mobile: [{ required: true, validator: validateMobile, trigger: 'blur' }],
    address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
    sex: [{ required: true, message: '请选择性别', trigger: 'blur' }]
  })

  /**
   * 性别选项
   */
  const options = [
    { value: '1', label: '男' },
    { value: '2', label: '女' }
  ]

  /**
   * 用户标签列表
   */
  const lableList: Array<string> = ['专注设计', '很有想法', '辣~', '大长腿', '川妹子', '海纳百川']

  onMounted(() => {
    syncFormWithUserInfo()
    loadLatestUserInfo()
  })

  watch(
    () => userInfo.value,
    () => {
      if (!isEdit.value) {
        syncFormWithUserInfo()
      }
    },
    { deep: true }
  )

  const syncFormWithUserInfo = () => {
    const currentUser = userInfo.value || {}
    form.realName = currentUser.realName || currentUser.userName || ''
    form.nikeName = currentUser.nickName || currentUser.userName || ''
    form.email = currentUser.email || ''
    form.mobile = currentUser.mobile || ''
    form.sex = currentUser.userGender || ''
    form.address = currentUser.address || ''
    form.des = currentUser.des || ''
  }

  const loadLatestUserInfo = async () => {
    try {
      const latest = await fetchGetUserInfo()
      userStore.setUserInfo({
        ...(userStore.getUserInfo as Api.Auth.UserInfo),
        ...latest
      } as Api.Auth.UserInfo)
      syncFormWithUserInfo()
    } catch (error) {
      console.error('获取最新个人信息失败:', error)
    }
  }

  /**
   * 切换用户信息编辑状态
   */
  const edit = async () => {
    if (!isEdit.value) {
      isEdit.value = true
      return
    }

    if (!ruleFormRef.value) {
      return
    }

    try {
      await ruleFormRef.value.validate()
      saving.value = true

      const latest = await fetchUpdateUserProfile({
        realName: form.realName,
        nickName: form.nikeName,
        email: form.email,
        mobile: form.mobile,
        address: form.address,
        userGender: form.sex,
        des: form.des
      })

      userStore.setUserInfo({
        ...(userStore.getUserInfo as Api.Auth.UserInfo),
        ...latest
      } as Api.Auth.UserInfo)

      isEdit.value = false
      ElMessage.success('保存成功')
    } catch (error) {
      if (error instanceof HttpError) {
        ElMessage.error(error.message)
      } else {
        ElMessage.error('保存个人信息失败，请稍后重试')
        console.error('保存个人信息失败:', error)
      }
    } finally {
      saving.value = false
    }
  }

  const goChangePassword = () => {
    router.push('/change-password')
  }

  const cancelEdit = () => {
    syncFormWithUserInfo()
    ruleFormRef.value?.clearValidate()
    isEdit.value = false
  }

  const beforeAvatarUpload = (file: File) => {
    const isImage = file.type.startsWith('image/')
    const isLt5M = file.size / 1024 / 1024 <= AVATAR_MAX_SIZE_MB

    if (!isImage) {
      ElMessage.error('仅支持上传图片文件')
      return false
    }

    if (!isLt5M) {
      ElMessage.error(`头像大小不能超过 ${AVATAR_MAX_SIZE_MB}MB`)
      return false
    }

    return true
  }

  const handleAvatarUpload = async (options: UploadRequestOptions) => {
    try {
      avatarUploading.value = true
      const result = await fetchUploadUserAvatar(options.file)
      userStore.setUserInfo({
        ...(userStore.getUserInfo as Api.Auth.UserInfo),
        avatar: result.url
      } as Api.Auth.UserInfo)
      options.onSuccess?.(result)
      ElMessage.success('头像更新成功')
    } catch (error) {
      options.onError?.(error as UploadAjaxError)
      ElMessage.error('头像更新失败')
    } finally {
      avatarUploading.value = false
    }
  }
</script>
