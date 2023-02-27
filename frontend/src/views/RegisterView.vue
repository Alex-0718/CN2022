<template>
    <v-container>
        <v-card>
            <v-card-title>註冊</v-card-title>
            <v-container class="tw-pt-0">
                <v-form ref="form">
                    <v-text-field label="username" v-model="form.username" :rules="required"></v-text-field>
                    <v-text-field label="password" type="text" v-model="form.password" :rules="required"></v-text-field>
                    <v-btn color="primary" @click="register()" :loading="registering">註冊</v-btn>
                </v-form></v-container>
        </v-card>

        <router-link to="/">
            <span class="tw-mt-2 tw-text-center tw-w-full tw-inline-block">阿其實我註冊過了拉, 派謝</span></router-link>
    </v-container>
</template>
<script>
export default {
    name: 'RegisterView',
    data() {
        return {
            form: {
                username: '',
                password: ''
            },
            registering: false,
            required: [
                (value) => {
                    if (value instanceof String) return value?.trim().length ? true : "必填";
                    else if (value instanceof Number) return true;
                    else return !!value ? true : "必填";
                },
            ],
        }
    },
    methods: {
        register() {
            this.registering = true
            fetch(process.env.VUE_APP_API + '/register', {
                method: 'POST',
                credentials: 'include',
                body: JSON.stringify(this.form),
                headers: {
                    'content-type': 'application/json'
                }
            }).then(r => r.json()).then(response => {
                if (response.success) {
                    alert('註冊成功 請登入')
                    this.$router.push('/')
                }
                else alert(response.data)
                this.form.username = ''
                this.form.password = ''
                this.registering = false
            })
        },
    }
}</script>