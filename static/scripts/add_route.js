import { isIP, isRange } from 'range_check';
import React, { Component } from 'react'
import { Form, Button, Row, } from 'react-bootstrap';
import { Typeahead } from 'react-bootstrap-typeahead';
import 'react-bootstrap-typeahead/css/Typeahead.css';
import baseURL from './baseURL.json'

class AddRoute extends Component {
    token;
    addRouteCloser;
    route;
    constructor(props) {
        super(props);

        this.token = props.token;
        this.addRouteCloser = props.addRouteCloser;
        this._isMounted = false;

        if (props.route) {
            this.route = props.route;

            this.state = {
                isEditing: true,
                service_names: [],
                routeAction: this.route.route_action,
                _in: this.route._in ? this.route._in : "",
                in_on: this.route.in_on ? this.route.in_on : "",
                isIngress: this.route._in == "in" ? true : false,
                _out: this.route._out ? this.route._out : "",
                out_on: this.route.out_on ? this.route.out_on : "",
                isEgress: this.route._out == "out" ? true : false,
                from_IP: this.route.from_IP ? this.route.from_IP : "any",
                from_port: this.route.from_port ? this.route.from_port : undefined,
                isFromServiceName: false,
                from_service_name: this.route.from_service_name ? [{ name: this.route.from_service_name }] : [{ name: "" }],
                to_IP: this.route.to_IP ? this.route.to_IP : "any",
                to_port: this.route.to_port ? this.route.to_port : undefined,
                isToServiceName: false,
                to_service_name: this.route.to_service_name ? { name: this.route.to_service_name } : [{ name: "" }],
                protocol: this.route.protocol ? this.route.protocol : "udp/tcp",
                comment: this.route.comment ? this.route.comment : ""
            }

        } else {
            this.state = {
                isEditing: false,
                service_names: [],
                routeAction: 'allow',
                _in: "",
                in_on: "",
                isIngress: false,
                _out: "",
                out_on: "",
                isEgress: false,
                from_IP: undefined,
                from_port: undefined,
                isFromServiceName: false,
                from_service_name: [{ name: "" }],
                to_IP: undefined,
                to_port: undefined,
                isToServiceName: false,
                to_service_name: [{ name: "" }],
                protocol: "udp/tcp",
                comment: ""
            }
        }


    }

    get_service_name = () => {
        fetch(baseURL.url + 'get_services', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.token
                    }`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }).then(
            response => {
                if (response.status === 401) {
                    sessionStorage.clear()
                    window.location.replace("/")
                }
                // TODO add this to app level
                if (response.status === 403) {
                    this.strike++;
                    console.log(this.strike)
                    if (this.strike >= 3) {
                        sessionStorage.clear()
                        window.location.replace("/")
                    }
                }
                return response.json()
            }).then(
                data => {
                    this._isMounted && this.setState({
                        service_names: data.result,
                    })
                });
    }
    addRoute = () => {
        if (this._isMounted) {
            let body = {
                route_action: this.state.routeAction,
            }
            body["from_IP"] = (isIP(this.state.from_IP)
                || isRange(this.state.from_IP)) ? this.state.from_IP : "any";

            if (this.state.isIngress) {
                body["_in"] = this.state._in
                if (this.state.in_on != null) {
                    body["in_on"] = this.state.in_on
                }
            }
            if (this.state.isEgress) {
                body["_out"] = this.state._in
                if (this.state.in_on != null) {
                    body["out_on"] = this.state.out_on
                }
            }
            if (!this.state.isFromServiceName) {
                body["from_port"] = this.state.from_port;
            } else {
                body["from_service_name"] = this.state.from_service_name[0].name
            }

            body["to_IP"] = (isIP(this.state.to_IP)
                || isRange(this.state.to_IP)) ? this.state.to_IP : "any";

            if (!this.state.isToServiceName) {
                body["to_port"] = this.state.to_port;
            } else {
                body["to_service_name"] = this.state.to_service_name[0].name
            }
            if (this.state.protocol !== "udp/tcp")
                body["protocol"] = this.state.protocol;
            if (this.state.comment !== "")
                body["comment"] = this.state.comment;

            fetch(baseURL.url + 'add_route', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token
                        }`,
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            }).then(
                response => {
                    if (response.status === 401) {
                        sessionStorage.clear()
                        window.location.replace("/")
                    }
                    // TODO add this to app level
                    if (response.status === 403) {
                        this.strike++;
                        console.log(this.strike)
                        if (this.strike >= 3) {
                            sessionStorage.clear()
                            window.location.replace("/")
                        }
                    }
                    return response.json()
                }).then(
                    data => {
                        this._isMounted && this.setState({
                            message: data.result,
                            currentPassword: "",
                            newPassword: "",
                            confirmNewPassword: "",
                            isLoading: false
                        }, this.addRouteCloser())
                    });

        }

    }

    reset = () => {
        this._isMounted && this.setState({
            isEditing: false,
            routeAction: 'allow',
            _in: "",
            in_on: "",
            isIngress: false,
            _out: "",
            out_on: "",
            isEgress: false,
            from_IP: undefined,
            from_port: undefined,
            isFromServiceName: false,
            from_service_name: [{ name: "" }],
            to_IP: undefined,
            to_port: undefined,
            isToServiceName: false,
            to_service_name: [{ name: "" }],
            protocol: "udp/tcp",
            comment: ""
        }, this.addRouteCloser())

    }

    componentDidMount() {
        this._isMounted = true;
        this.get_service_name()
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render() {
        return (
            < Form id="addRouteForm"
                onSubmit={this.addRoute}
                onReset={this.reset}>
                <Form.Group controlId="addRouteForm.RouteAction">
                    <Form.Label>Route Action:</Form.Label>
                    <Form.Control
                        as="select"
                        disabled={this.state.isEditing}
                        defaultValue={this.state.routeAction}
                        onChange={element => {
                            this.setState({ routeAction: element.currentTarget.value })
                        }}>
                        <option>allow</option>
                        <option>deny</option>
                        <option>reject</option>
                        <option>limit</option>
                    </Form.Control>
                </Form.Group>

                <Form.Group controlId="addRouteForm.from_IP">
                    <Form.Label>From IP:</Form.Label>
                    <Form.Control
                        type="input"
                        disabled={this.state.isEditing}
                        defaultValue={this.state.from_IP}
                        placeholder="Enter ip address or 'any'"
                        onChange={element => {
                            this.setState({ from_IP: element.currentTarget.value })
                        }} />
                </Form.Group>


                <Form.Check
                    id="addRouteForm._in"
                    type="switch"
                    label="Ingress Filtering"
                    disabled={this.state.isEditing}
                    checked={this.state.isIngress}
                    onChange={element => {
                        this.setState({
                            _in: element.currentTarget.checked ? "in" : "",
                            isIngress: element.currentTarget.checked

                        })
                    }}
                />
                {this.state.isIngress &&
                    <Form.Group controlId="addRouteForm.in_on">
                        <Form.Label>Ingress Network Interface:</Form.Label>
                        <Form.Control
                            placeholder="enter network interface name for example: eth0 or wlan0"
                            disabled={this.state.isEditing}
                            defaultValue={this.state.in_on}
                            onChange={element => {
                                this.setState({ in_on: element.currentTarget.value })
                            }} />
                    </Form.Group>
                }
                <Form.Check
                    id="addRouteForm._out"
                    type="switch"
                    label="Egress Filtering"
                    disabled={this.state.isEditing}
                    checked={this.state.isEgress}
                    onChange={element => {
                        this.setState({
                            _out: element.currentTarget.checked ? "out" : "",
                            isEgress: element.currentTarget.checked

                        })
                    }}
                />
                {this.state.isEgress &&
                    <Form.Group controlId="addRouteForm.out_on">
                        <Form.Label>Egress Network Interface:</Form.Label>
                        <Form.Control
                            placeholder="enter network interface name for example: eth0 or wlan0"
                            disabled={this.state.isEditing}
                            defaultValue={this.state.out_on}
                            onChange={element => {
                                this.setState({ out_on: element.currentTarget.value })
                            }} />
                    </Form.Group>
                }
                <Form.Check
                    id="addRouteForm.is_from_service_name"
                    type="switch"
                    label="Use Service Name For Source"
                    disabled={this.state.isEditing}
                    checked={this.state.isFromServiceName}
                    onChange={element => {
                        this.setState({ isFromServiceName: element.currentTarget.checked })
                    }}
                />
                {this.state.isFromServiceName ?
                    <Form.Group controlId="addRouteForm.from_service_name">
                        <Form.Label>From Service Name:</Form.Label>
                        <Typeahead
                            id="from_service_name"
                            disabled={this.state.isEditing}
                            labelKey="name"
                            onChange={
                                value => {
                                    this.setState({ from_service_name: value })
                                }
                            }
                            options={this.state.service_names}
                            placeholder="Choose a service..."
                            defaultSelected={this.state.from_service_name}
                        />
                    </Form.Group>
                    :
                    <Form.Group controlId="addRouteForm.from_port">
                        <Form.Label>From Port:</Form.Label>
                        <Form.Control
                            placeholder="enter port number for example: 80 or 'any'"
                            disabled={this.state.isEditing}
                            defaultValue={this.state.from_port}
                            onChange={element => {
                                this.setState({ from_port: element.currentTarget.value })
                            }} />
                    </Form.Group>
                }

                <Form.Group controlId="addRouteForm.to_IP">
                    <Form.Label>To IP:</Form.Label>
                    <Form.Control
                        type="input"
                        disabled={this.state.isEditing}
                        defaultValue={this.state.to_IP}
                        placeholder="Enter ip address or 'any'"
                        onChange={element => {
                            this.setState({ to_IP: element.currentTarget.value })
                        }} />
                </Form.Group>

                <Form.Check
                    id="addRouteForm.is_to_service_name"
                    type="switch"
                    label="Use Service Name For Destination"
                    disabled={this.state.isEditing}
                    checked={this.state.isToServiceName}
                    onChange={element => {
                        this.setState({ isToServiceName: element.currentTarget.checked })
                    }}
                />
                {this.state.isToServiceName ?
                    <Form.Group controlId="addRouteForm.to_service_name">
                        <Form.Label>From Service Name:</Form.Label>
                        <Typeahead
                            id="to_service_name"
                            disabled={this.state.isEditing}
                            labelKey="name"
                            onChange={
                                value => {
                                    this.setState({ to_service_name: value })
                                }
                            }
                            options={this.state.service_names}
                            placeholder="Choose a service..."
                            defaultSelected={this.state.to_service_name}
                        />
                    </Form.Group>
                    :
                    <Form.Group controlId="addRouteForm.to_port">
                        <Form.Label>To Port:</Form.Label>
                        <Form.Control
                            placeholder="enter port number for example: 80 or 'any'"
                            disabled={this.state.isEditing}
                            defaultValue={this.state.to_port}
                            onChange={element => {
                                this.setState({ to_port: element.currentTarget.value })
                            }} />
                    </Form.Group>
                }

                <Form.Group controlId="addRouteForm.protocol">
                    <Form.Label>Protocol:</Form.Label>
                    <Form.Control
                        as="select"
                        disabled={this.state.isEditing}
                        defaultValue={this.state.protocol}
                        onChange={element => {
                            this.setState({ protocol: element.currentTarget.value })
                        }}>
                        <option>tcp/udp</option>
                        <option>tcp</option>
                        <option>udp</option>
                        <option>ah</option>
                        <option>esp</option>
                        <option>gre</option>
                        <option>ipv6</option>
                        <option>igmp</option>
                    </Form.Control>
                </Form.Group>

                <Form.Group controlId="addRouteForm.Comment">
                    <Form.Label>Comment:</Form.Label>
                    <Form.Control
                        as="textarea" rows={3}
                        defaultValue={this.state.comment}
                        onChange={element => {
                            this.setState({ comment: element.currentTarget.value })
                        }} />
                </Form.Group>
                <Row className="justify-content-md-center buttons-box-wrapper">
                    <Button
                        variant="success"
                        type="submit">
                        Add Route
                </Button>
                    <Button
                        variant="danger"
                        type="reset">
                        Reset
                </Button>
                </Row>

            </Form >
        );
    }

};

export default AddRoute;