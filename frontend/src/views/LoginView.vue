<template>
  <v-container>
    <v-card>
      <v-card-title>登入</v-card-title>
      <v-container class="tw-pt-0">
        <v-form ref="form">
          <v-text-field label="username" v-model="form.username" :rules="required"></v-text-field>
          <v-text-field label="password" type="text" v-model="form.password" :rules="required"></v-text-field>
          <v-btn color="primary" @click="login()" :loading="loggingIn">登入</v-btn>
        </v-form></v-container>
    </v-card>

    <router-link to="/register">
      <span class="tw-mt-2 tw-text-center tw-w-full tw-inline-block">沒有帳號？點這裡註冊</span></router-link>
  </v-container>
</template>
<script>
export default {
  name: 'LoginView',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      loggingIn: false,
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
    login() {
      this.loggingIn = true
      fetch(process.env.VUE_APP_API + '/login', {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(this.form),
        headers: {
          'content-type': 'application/json'
        }
      }).then(r => r.json()).then(response => {
        if (response.success) {
          this.$store.commit('login', { username: this.form.username })
          if (this.$route.name != 'post') this.$router.push('/post')
        }
        else alert(response.data)
        this.form.username = ''
        this.form.password = ''
        this.loggingIn = false
      })
    },
  }
}</script>