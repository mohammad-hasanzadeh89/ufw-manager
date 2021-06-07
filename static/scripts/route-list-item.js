import React, { Component } from 'react'
import { Button } from 'react-bootstrap';
import '../css/app.css';
class RouteListItem extends Component {
    constructor(props) {
        super(props);

        this.state = {
            route: props.route,
            deleteConfirmOpener: props.deleteConfirmOpener,
            editRoute: props.editRoute
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
                <td>{route.user_id.toString()}</td>
                <td>{route.route_command}</td>
                <td>{route.route_action}</td>
                <td>{route._in}</td>
                <td>{route.in_on}</td>
                <td>{route._out}</td>
                <td>{route.out_on}</td>
                <td>{route.from_IP.toString()}</td>
                <td>{route.from_port.toString()}</td>
                <td>{route.from_service_name}</td>
                <td>{route.to_IP.toString()}</td>
                <td>{route.to_port.toString()}</td>
                <td>{route.to_service_name}</td>
                <td>{route.protocol.toString()}</td>
                <td>{route.comment}</td>
                <td>{route.add_date}</td>
                <td>
                    <Button
                        style={{ marginRight: '1rem' }}

                        variant="warning"
                        onClick={
                            () => { this.state.editRoute(this.state.route) }}>
                        Edit
                    </Button>
                    <Button
                        variant="danger"
                        onClick={
                            () => { this.state.deleteConfirmOpener(this.state.route) }}>
                        Delete
                    </Button>
                </td>

            </tr>


        );
    }

};

export default RouteListItem;