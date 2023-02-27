<template>
    <div class="tw-flex tw-flex-row tw-h-16 tw-items-center tw-px-4 tw-bg-primary tw-text-white">
        <h1 class="tw-flex-1 tw-text-left tw-text-2xl">Messaging</h1>
        <div v-if="$store.state.loggedIn">
            <span class="px-1">Hi, {{ $store.state.username }}</span>
            <span class="px-1" @click="logout">登出</span>
        </div>
        <div v-else>
            <router-link to="/" class="tw-text-white">
                <span>請先登入</span>
            </router-link>
        </div>
    </div>
</template>
<script>
export default {
    name: 'Header',
    data() {
        return {
            loginDialog: false,
            loggingIn: false,
            form: {
                username: '',
                password: ''
            }
        }
    },
    methods: {
        logout() {
            fetch(process.env.VUE_APP_API + '/logout', {
                credentials: 'include'
            }).then(r => r.json()).then(response => {
                if (response.success) {
                    this.$store.commit('logout')
                    this.$router.push('/')
                }
                else alert(response.data)
            })
        }
    }
}
</script>