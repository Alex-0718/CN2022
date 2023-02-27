<template>
    <v-container>
        <video ref="originVideo" controls muted autoplay class="tw-rounded-xl tw-mb-4"></video>
        <video ref="remoteVideo" controls muted autoplay class="tw-rounded-xl tw-mb-4"></video>
        <div v-if="initializing">
            <v-progress-circular indeterminate color="primary"></v-progress-circular> 初始化連線...
        </div>
        <template v-else-if="!connected">
            <v-list v-if="contactList.length">
                <v-list-item v-for="contact, index in contactList" :key="`contact${index}`"
                    @click="connectRequest(contact)">
                    <v-list-item-content>
                        <v-list-item-title>{{ contact.username }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list>
            <div v-else>
                <p>目前沒有其他人上線，請你的朋友也打開這個頁面</p>
                <p>其實沒有朋友也沒有關係, 可以對著鏡子視訊</p>
            </div>
            <v-btn color="primary" @click="fetchContacts()">刷新列表</v-btn>
        </template>
    </v-container>
</template>

<script>

export default {
    name: 'Phoneview',
    data() {
        return {
            contacts: [],
            peer: undefined,
            sdp: undefined,
            candidates: [],
            initializing: true,
            localStream: undefined,
            connected: false,
        }
    },
    mounted() {
        this.setupRTC()
    },
    methods: {
        async send(obj) {
            return fetch(process.env.VUE_APP_API + '/phonebook', {
                credentials: 'include',
                method: 'POST',
                body: JSON.stringify(obj),
                headers: {
                    'content-type': 'application/json'
                }
            }).then(r => r.json()).then(response => {
                console.log(response)
            })
        },
        async fetchContacts() {
            return fetch(process.env.VUE_APP_API + '/phonebook', { credentials: 'include' }).then(r => r.json()).then(response => {
                if (response.success) {
                    this.contacts = response.data
                }
                else alert(response.data)
            })
        },
        async setupRTC() {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            })
            
            setTimeout(() => { this.initializing = false }, 3000)

            this.localStrem = stream
            this.$refs.originVideo.srcObject = stream
            this.peer = new RTCPeerConnection({
                iceServers: [{
                    url: "stun:stun.l.google.com:19302"
                }, {
                    url: "turn:140.112.30.32:3478",
                    username: "username",
                    credential: "password"
                }]
            })
            this.peer.addStream(stream);
            this.peer.onaddstream = (event) => {
                this.$refs.remoteVideo.srcObject = event.stream;
                this.connected = true
                this.finished = true
            }

            this.peer.onicecandidate = (event) => {
                if (event.candidate) {
                    this.candidates.push(event.candidate)
                } else {
                    this.initializing = false
                }
            }

            this.sdp = await this.peer.createOffer({
                offerToReceiveAudio: 1,
                offerToReceiveVideo: 1
            })

            this.peer.setLocalDescription(this.sdp);

        },
        connectRequest(contact) {
            this.peer.setRemoteDescription(contact.sdp, () => {
                this.peer.createAnswer().then((desc) => {
                    this.peer.setLocalDescription(desc, () => {
                        console.log(this.peer.localDescription, this.candidates)
                        console.log('123')
                        this.send({
                            username: this.$store.state.username,
                            sdp: this.peer.localDescription,
                            candidates: this.candidates,
                            target: contact.username
                        })
                    });
                });
            });
            contact.candidates.forEach(candidate => {
                this.peer.addIceCandidate(candidate)
            })
        },
        async pollingIncoming() {
            if (this.connected) return
            await fetch(process.env.VUE_APP_API + '/phonebook', { credentials: 'include' }).then(r => r.json()).then(response => {
                if (response.success) {
                    response.data.filter(item => item.sdp.type == 'answer' && item.target == this.$store.state.username).forEach(item => {

                        if (confirm(`您要跟${item.username}連線嗎？`)) {
                            this.peer.setRemoteDescription(item.sdp)
                            item.candidates.forEach(candidate => {
                                this.peer.addIceCandidate(candidate)
                            })

                            this.connected = true

                            const params = [this.$store.state.username, item.username]
                            params.forEach(username => {
                                fetch(process.env.VUE_APP_API + '/phonebook', {
                                    credentials: 'include',
                                    method: 'DELETE',
                                    body: JSON.stringify({
                                        username
                                    }),
                                    headers: {
                                        'content-type': 'application/json'
                                    }
                                }).then(r => r.json()).then(response => {
                                    if (!response.success) alert(response.data)
                                })
                            })

                            return
                        }
                    })
                }
                else alert(response.data)
            })
            setTimeout(this.pollingIncoming, 1000)
        }
    },
    computed: {
        contactList() {
            return this.contacts.filter(item => item.username != this.$store.state.username)
        }
    },
    watch: {
        initializing(newVal) {
            if (newVal == false) {
                console.log(this.candidates)
                this.send({
                    username: this.$store.state.username,
                    sdp: this.sdp,
                    target: '',
                    candidates: this.candidates
                }).then(() => {
                    this.fetchContacts().then(() => {
                        this.pollingIncoming()
                    })
                })
            }
        }
    },
}
</script>