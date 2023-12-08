<template>
  <TopNavbar></TopNavbar>
  <ClientOnly>
    <FirstLogin v-if="login_type == 'first'"></FirstLogin>
    <NewFlow v-else></NewFlow>
  </ClientOnly>
</template>

<script>
export default {
  data() {
    return {
      user_data: null,
      login_type: null,
    };
  },
  created() {},
  mounted() {
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"));
    if (this.user_data == null) {
      this.$router.push("/Login");
      return;
    }
    if (
      Boolean(this.user_data.login_history) &&
      this.user_data.login_history.length > 0
    ) {
    } else {
      this.login_type = "first";
    }
  },

  methods: {
    async loginToSpotify() {
      try {
        const response = await fetch("http://10.9.0.6/user/user-auth-url", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: this.user_data.user_id,
          }),
        });
        if (!response.ok) {
          throw new Error("Failed to Login");
        }
        const responseData = await response.json();
        console.log({ responseData });
        window.location.href = responseData.url;
        // if (responseData.length > 0) {
        //   this.show_music_player = true;
        //   this.songs_list = responseData;
        // } else {
        //   this.show_music_player = true;
        //   this.songs_list = random_songs;
        // }
      } catch (error) {
        console.log(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
    logoutAccount() {
      sessionStorage.clear();
      this.$router.go("/Login");
    },
  },
};
</script>

<style>
</style>