<template>
    <v-container>
        <v-dialog v-model="dialog" persistent max-width="600px">
            <template v-slot:activator="{ on, attrs }">
                <v-btn color="primary" dark v-bind="attrs" v-on="on">
                    新貼文
                </v-btn>
            </template>
            <v-card>
                <v-card-title>
                    <span class="text-h5">新增貼文</span>
                </v-card-title>
                <v-card-text>
                    <v-container>
                        <v-text-field label="標題" v-model="form.title"></v-text-field>
                        <v-textarea label="內容" v-model="form.content"></v-textarea>
                    </v-container>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" @click="dialog = false"> Close </v-btn>
                    <v-btn color="primary" @click="post(); dialog = false" :loading="saving"> Save </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
        <v-card v-for="(post, index) in posts" :key="`post${index}`" class="my-2">
            <v-card-text class="markdown-body" v-html="markdown(post)">
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
const marked = require('marked')

export default {
    name: 'PostView',
    data() {
        return {
            posts: [],
            dialog: false,
            form: {
                title: '',
                content: ''
            },
            saving: false
        }
    },
    mounted() {
        this.fetchPost()
    },
    methods: {
        fetchPost() {
            fetch(process.env.VUE_APP_API + '/bulletin', { credentials: 'include' }).then(r => r.json()).then(response => {
            if (response.success) {
                this.posts = response.data
            }
            else alert(response.data)
        })
        },
        markdown({content, title, username}) {
            return marked.parse(`
# ${title}
> 發文者: ${username}

${content}
            `)
        },
        post() {
            this.saving = true
            fetch(process.env.VUE_APP_API + '/bulletin', {
                credentials: 'include',
                method: 'POST',
                body: JSON.stringify(this.form),
                headers:{
                    'content-type': 'application/json'
                }
            }).then(r => r.json()).then(response => {
                if (response.success) {
                    this.fetchPost()
                } else {
                    alert(response.data)
                }
                this.saving = false
            })
        }
    }
}
</script>