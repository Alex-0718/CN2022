import Vue from 'vue'
import VueRouter from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PostView from '../views/PostView.vue'
import PhoneView from '../views/PhoneView.vue'

Vue.use(VueRouter)

const routes = [{
        path: '/',
        name: 'login',
        component: LoginView
    },
    {
        path: '/post',
        name: 'post',
        component: PostView
    },
    {
        path: '/phone',
        name: 'phone',
        component: PhoneView
    },
    {
        path: '/register',
        name: 'register',
        component: RegisterView
    }
]

const router = new VueRouter({
    routes
})

export default router