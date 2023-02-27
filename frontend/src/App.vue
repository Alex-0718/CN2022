<template>
  <v-app id="app" class="tw-h-screen tw-flex tw-flex-col">
    <Header class="tw-shadow-[0_0_3px_0_#0004]"></Header>
    <router-view class="tw-flex-1 tw-overflow-y-scroll" />
    <Navigation class="tw-shadow-[0_0_3px_0_#0004]"></Navigation>
  </v-app>
</template>

<script>
import Header from './components/Header.vue'
import Navigation from './components/Navigation.vue';
export default {
  name: 'App',
  components: {
    Header,
    Navigation
  },
  mounted() {
    console.log(process.env.VUE_APP_API)
    fetch(process.env.VUE_APP_API + '/status', {
      credentials: 'include'
    }).then(r => r.json()).then(response => {
      if (response.success) {
        if (response.data.username) {
          this.$store.commit('login', { username: response.data.username })
          if (this.$route.name == 'login') this.$router.push('/post')
        } else {
          this.$router.push('/')
        }
      } else {
        alert(response.data)
      }
    })
  }
}
</script>