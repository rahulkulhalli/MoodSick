<template>
    <div>
      <h1>
        Model History parameters according to mood selection
      </h1>
      <div id="main" style="height:80vh; width:80vw"></div>
      <select v-model="selectedMood" @change="updateChart">
        <option value="very_sad">Very Sad</option>
        <option value="sad">Sad</option>
        <option value="neutral">Neutral</option>
        <option value="happy">Happy</option>
        <option value="very_happy">Very Happy</option>
      </select>
    </div>
  </template>
  
  <script>
  import * as echarts from 'echarts';
  
  export default {
    data() {
      return {
        selectedMood: 'very_sad',
      };
    },
    mounted() {
      this.updateChart();
    },
    methods: {
      updateChart() {
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
  
        var option = {
          xAxis: {
            type: 'category',
            name: 'Model Features',
            data: ['target_danceability', 'target_energy', 'target_key', 'target_loudness', 'target_mode', 'target_speechiness', 'target_acousticness', 'target_instrumentalness', 'target_liveness', 'target_valence', 'target_tempo', 'target_time_signature'],
          },
          yAxis: {
            type: 'value',
            name: 'Values',
          },
          series: [
            {
              data: this.getMoodData(this.selectedMood),
              type: 'bar',
            },
          ],
        };
  
        option && myChart.setOption(option);
      },
      getMoodData(mood) {
        // Return data based on the selected mood
        switch (mood) {
          case 'very_sad':
            return [0.0, 0.118, 0.0, -0.08, 0.0, 0.0, 0.0, 0.0, 0.106, 0.137, 0.0, 1.0];
          // Add cases for other moods
          // case 'sad':
          //   return [...];
          // case 'neutral':
          //   return [...];
          // case 'happy':
          //   return [...];
          // case 'very_happy':
          //   return [...];
          default:
            return [];
        }
      },
    },
  };
  </script>
  
  <style>
  </style>
  


<!-- option = {
    xAxis: {
      type: 'category',
      data: ['target_danceability', 'target_energy', 'target_key', 'target_loudness', 'target_mode', 'target_speechiness', 'target_acousticness', 'target_instrumentalness', 'target_liveness', 'target_valence', 'target_tempo', 'target_time_signature']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [0.0, 0.118, 0.0, -0.08, 0.0, 0.0, 0.0, 0.0, 0.106, 0.137, 0.0, 1.0],
        type: 'bar'
      }
    ]
  };
   -->