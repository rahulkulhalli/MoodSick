<template>
  Genre Count
  <div id="main" style="height: 80vh; width: 100%"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: ["graphData"],
  mounted() {
    // console.log(this.graphData);
    var chartDom = document.getElementById("main");
    var myChart = echarts.init(chartDom);
    var option;
    let data = [];
    for (let key in this.graphData) {
      data.push({
        value: this.graphData[key],
        name: key,
      });
    }
    // console.log(data);
    option = {
    //   title: {
    //     text: "Referer of a Website",
    //     subtext: "Fake Data",
    //     left: "center",
    //   },
      tooltip: {
        trigger: "item",
      },
      legend: {
        orient: "vertical",
        left: "left",
      },
      series: [
        {
          name: "Access From",
          type: "pie",
          radius: "50%",
        //   top: '-20%',
        //     left: '-20%',
    //   right: '-20%',
    //   bottom: '-20%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0, 0, 0, 0.5)",
            },
          },
        },
      ],
    };

    option && myChart.setOption(option);
  },
};
</script>

<style></style>



<!-- 
option = {
    xAxis: {
      type: 'category',
      name: 'Genres',
      data: ['rock', 'hip-hop', 'blues', 'classical', 'metal', 'reggae', 'country', 'pop', 'disco']
    },
    yAxis: {
      type: 'value',
      name: 'Count'
    },
    series: [
      {
        data: [2, 1, 1, 0, 1, 1, 0, 1, 1],
        type: 'line'
      }
    ]
  }; -->