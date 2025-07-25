import React from 'react';
import Info from "./components/Info";
import Form from "./components/Form";
import Weather from "./components/Weather";

const API_KEY = "98dee64db2df4e62cc8ed3cfa06caf50";

class App extends React.Component {

    state = {
        temp: undefined,
        city: undefined,
        country: undefined,
        sunrise: undefined,
        sunset: undefined,
        error: undefined
}

    gettingWeather = async (e) => {
        if (e.preventDefault) {
            e.preventDefault();
        }
        let city = "";
        if (e.target.elements && e.target.elements.city) {
            city = e.target.elements.city.value;
        } else if (e.target.value) {
            city = e.target.value;
        }
      const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&units=metric`);
      const data = await response.json();
      console.log(data);

      if (city && response.ok) {
          this.setState({
              temp: data.main.temp,
              city: data.name,
              country: data.sys.country,
              sunrise: data.sys.sunrise,
              sunset: data.sys.sunset,
              error: ""
          });
      } else if (!response.ok) {
          this.setState({
              temp: undefined,
              city: undefined,
              country: undefined,
              sunrise: undefined,
              sunset: undefined,
              error: "че за фигню ты мне пишешь"
          });
      }
    }


    render() {
        const { temp } = this.state;
        let weatherClass = "";
        if (typeof temp === "number") {
            if (temp > 0) weatherClass = "sunny";
            else if (temp < 0) weatherClass = "snowy";
        }
        return (
            <div className={`wrapper ${weatherClass}`}> 
                <div className="main">
                    <div className="container">
                        <div className="row">
                            <div className="col-5 info">
                                <Info />
                            </div>
                            <div className="col-7 form">
                                <Form weatherMethod={this.gettingWeather} />
                                <Weather
                                    temp={this.state.temp}
                                    city={this.state.city}
                                    country={this.state.country}
                                    pressure={this.state.pressure}
                                    sunset={this.state.sunset}
                                    error={this.state.error}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );

    }
}

export default App;
