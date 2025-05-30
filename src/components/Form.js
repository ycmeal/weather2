import React from 'react';

class Form extends React.Component {
    handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            this.props.weatherMethod(e);
        }
    }

    render() {
        return (
            <form onSubmit={this.props.weatherMethod}>
                <input type="text" name="city" placeholder="City" required onKeyDown={this.handleKeyDown} />
                <button type="submit">get weather</button>
            </form>
        );
    }
}

export default Form;
