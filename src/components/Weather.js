import React from 'react';

class Weather extends React.Component {
    render() {
        return (
            <div className="infoWeath">
                {this.props.error && <p className="error">{this.props.error}</p>}
                { this.props.city &&
                    <>
                    <p>Location: {this.props.city}, {this.props.country}</p>
                    <p className="temp">{this.props.temp}&#8451;</p>
                    </>
                }
            </div>
        );
    }
}

export default Weather;
