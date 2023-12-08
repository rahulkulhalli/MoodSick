<template>
  <div v-if="showGraphs" class="container">
    <div class="row">
        <div class="col-sm-4">
            <DateFrequency :graphData="DateFreqData"></DateFrequency>
        </div>
        <div class="col-sm-4">
            <DayFrequency :graphData="DayFrequencyData"></DayFrequency>
        </div>
        <div class="col-sm-4">
            <HourlyFrequency :graphData="HourlyFrequencyData"></HourlyFrequency>
        </div>
      <div class="col-sm-6">
        <GenreCount :graphData="GenreCountData"></GenreCount>
      </div>

      <div class="col-sm-6">
        <AggregateInputratings
          :graphData="AggregateInputratingsData"
        ></AggregateInputratings>
      </div>
      <div class="col-sm-6">
        <ModelParamHistory :graphData="ModelParamHistoryData"></ModelParamHistory>
      </div>
      <div class="col-sm-6">
        <SpotifyParamHistory :graphData="SpotifyParamHistoryData"></SpotifyParamHistory>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user_data: null,
      user_id: null,
      GenreCountData: null,
      AggregateInputratingsData: null,
      DateFreqData: null,
      DayFrequencyData: null,
      HourlyFrequency: null,
      HourlyFrequencyData: null,
      ModelParamHistoryData: null,
      SpotifyParamHistoryData: null,
      showGraphs: false,
    };
  },
  mounted() {
    this.user_data = JSON.parse(sessionStorage.getItem("user_data"));
    this.user_id = this.user_data.user_id;
    this.getGraphsData();
  },
  methods: {
    async getGraphsData() {
      try {
        const response = await fetch("http://10.9.0.6/user/viz", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: this.user_id,
          }),
        });
        const responseData = await response.json();
        this.GenreCountData = responseData.mood_viz.genre_frequency;
        this.AggregateInputratingsData = responseData.aggregate_input_ratings;
        this.DateFreqData = responseData.login_viz.date_freq;
        this.DayFrequencyData = responseData.login_viz.day_of_week_freq;
        this.HourlyFrequencyData = responseData.login_viz.hour_of_day_freq;
        this.ModelParamHistoryData = responseData.model_param_history;
        this.SpotifyParamHistoryData = responseData.spotify_param_history;
        this.showGraphs = true;
        // console.log(responseData);
        // if (responseData.message == "User Authorization Successful") {
        //   let user_data = JSON.parse(sessionStorage.getItem("user_data"));
        //   user_data["spotify_logged_in"] = true;
        //   sessionStorage.setItem("user_data", JSON.stringify(user_data));
        //   this.$router.push("/");
        // }
      } catch (error) {
        console.log(error);
        alert("Some Error Occurred! Pleaser Try Again!");
      }
    },
  },
};
</script>

<style scoped>
.container{
    background-image: linear-gradient(to right, #ffb6e5, #83a4d4) !important;

} 
</style>