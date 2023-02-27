import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        loggedIn: false,
        username: undefined
    },
    getters: {},
    mutations: {
        login(state, { username }) {
            state.username = username
            state.loggedIn = true
        },
        logout(state) {
            state.username = undefined
            state.loggedIn = false
        }
    },
    actions: {},
    modules: {}
})