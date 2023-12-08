<template>
Aggregate Input Ratings
  <div id="main23" style="height: 80vh; width: 100%"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  props: ["graphData"],

  mounted() {
    var chartDom = document.getElementById('main23');
    var myChart = echarts.init(chartDom);
    var option;
    let data = [];
    for (let key in this.graphData) {
      data.push({
        value: this.graphData[key],
        name: key,
      });
    }
    console.log(data);
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
          // top: '-20%',
          //   right: '-20%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: "rgba(0, 0, 0, 0.5)",
            },
          },
        },
      ],}

    option && myChart.setOption(option);

  }
}
</script>

<style></style>