import React, { Component } from 'react'

class DeletedRouteListItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            route: props.route
        }
    }

    cleanRouteFromNull = (obj) => {
        let temp = {}

        let keys = Object.keys(obj);
        for (let i = 0; i < keys.length; i++) {
            let key = keys[i]
            let val = obj[key]
            if (val === null)
                val = "null"
            temp[key] = val
        }
        return temp
    }

    render() {
        const route = this.cleanRouteFromNull(this.state.route)
        return (
            <tr>
                <td>{route.id.toString()}</td>
                <td>{route.route_command}</td>
                <td>{route.adder_user_id.toString()}</td>
                <td>{route.add_date}</td>
                <td>{route.deleter_user_id.toString()}</td>
                <td>{route.delete_date}</td>
            </tr>

        );
    }

};

export default DeletedRouteListItem;