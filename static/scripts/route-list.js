import React, { Component } from 'react'
import RouteListItem from './route-list-item';
import {
    Button, Modal, Container, Form,
    Row, Table, ListGroup, Badge, Spinner
} from 'react-bootstrap';
import Paginator from './paginator';
import AddRoute from './add_route';
import baseURL from './baseURL.json';
class RouteList extends Component {
    token;
    message;
    AdderId;
    queryInputs;
    constructor(props) {
        super(props);

        this.token = props.token;
        this.isAdmin = props.isAdmin;
        this.isManager = props.isManager;
        this.message = ""
        this.AdderId = undefined;
        this.queryInputs = [];

        this.state = {
            isLoading: false,
            showConfirmation: false,
            isAddingRoute: false,
            queryType: 0,
            routeType: "allow",
            routes: [],
            route: undefined,
            message: undefined,
            reports: [],
            activePage: 1,
            total: 0,
            pages: 0,
            perPage: 5
        };
    };

    addRouteCloser = (result = undefined) => {
        if (result) {
            this.state.reports.unshift(result)
        }
        this.setState({
            isAddingRoute: false,
            route: undefined,
            reports: this.state.reports
        })
        this.componentDidMount()
    }

    editRoute = (route) => {
        this.setState({
            isAddingRoute: true,
            route: route
        })
    }

    deleteConfirmOpener = (route) => {
        this.message = `Are you sure, you want to delete this route '${route.route_command}'`
        this.setState({ showConfirmation: true, route: route })
    }

    reject = () => {
        this.setState({ showConfirmation: false, route: undefined })
    }

    deleteRouteHandler = (routeId) => {
        this.setState({ isLoading: true })
        console.log(JSON.stringify({ routeId: routeId }))
        fetch(baseURL.url + 'delete_route_by_id', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token
                    }`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ routeId: routeId })
        }).then(
            response => response.json()).then(
                data => {
                    this.state.reports.unshift(data)
                    this.setState({
                        showConfirmation: false,
                        isLoading: false,
                        route: undefined,
                        reports: this.state.reports
                    })

                    this.componentDidMount()
                });
    }

    handlePageChange = (pageNumber) => {
        if (pageNumber > 0 && pageNumber <= this.state.pages &&
            pageNumber !== this.state.activePage) {
            this.getRoutes(pageNumber, this.state.perPage)
        }
    }

    queryInputsHandler = () => {
        this.queryInputs = [];

        let queryInput;
        switch (this.state.queryType) {
            case 1:
                queryInput = <Form.Group key="RouteType" controlId="setting.RouteType">
                    <Form.Label>Route Type:</Form.Label>
                    <Form.Control as="select"
                        defaultValue={this.state.routeType}
                        onChange={element => {
                            this.setState({ routeType: element.currentTarget.value })
                        }}>
                        <option>allow</option>
                        <option>deny</option>
                        <option>reject</option>
                        <option>limit</option>
                    </Form.Control>
                </Form.Group>
                break;
            case 2:
                queryInput = <Form.Group key="id" controlId="setting.AdderId">
                    <Form.Label>Id:</Form.Label>
                    <Form.Control placeholder="Adder Id"
                        defaultValue={this.AdderId}
                        onChange={element => {
                            this.AdderId = element.currentTarget.value
                        }} />
                </Form.Group>

                break;
            default:
                break
        }
        if (queryInput !== undefined) {
            this.queryInputs.push(queryInput)
        }
    }

    getRoutes = async (activePage, perPage) => {
        this.setState({ isLoading: true })
        let args = `?page=${activePage}` +
            `&perPage=${perPage}`
        let endPoint = "get_all_routes"
        switch (this.state.queryType) {
            case 1:
                args += `&routeAction=${this.state.routeType}`
                endPoint = "get_routes_by_type"
                break
            case 2:
                if (this.AdderId) {
                    args += `&userId=${this.AdderId}`
                    endPoint = "get_routes_by_user_id"
                }
                break
            default:
                break
        }
        fetch(
            baseURL.url + endPoint + args, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }).then(
            response => {
                if (response.ok) {
                    return response.json()
                }
                else {
                    if (response.status === 401) {
                        sessionStorage.clear()
                        window.location.replace("/")
                    }
                    console.log(response)
                    let alertMsg = response.status.toString()
                    alertMsg += " " + response.statusText
                    this.message = alertMsg
                    this.setState({
                        message: alertMsg,
                        isLoading: false,
                        activePage: 1,
                        total: 0,
                        pages: 0,
                        routes: [],
                    })
                    return undefined
                }
            }).then(
                data => {
                    if (data) {
                        this.setState({
                            message: undefined,
                            routes: data.result,
                            activePage: activePage,
                            total: data.total,
                            pages: Math.ceil(data.total / this.state.perPage),
                            perPage: perPage,
                            isLoading: false
                        })
                    }

                });
    }

    componentDidMount() {
        this.getRoutes(this.state.activePage, this.state.perPage)
    }

    render() {
        if (!this.isManager) {
            window.location.replace("/")
        }
        if (this.state.isLoading) {
            return (
                <Container fluid>
                    <Row className="center-screen">
                        <Spinner
                            className="spinner"
                            animation="border"
                            role="status">
                            <span className="sr-only">Loading...</span>
                        </Spinner>
                    </Row>
                </Container>
            )
        }
        this.queryInputsHandler(this.state.queryType)
        return (
            <Container fluid>
                <Row className="justify-content-md-center">
                    <h1>Routes</h1>
                </Row>
                {this.state.message !== undefined &&
                    <Row className="justify-content-md-center">
                        <h3>
                            <Badge
                                pill
                                variant="danger"
                            >*{this.state.message}</Badge>
                        </h3>
                    </Row>
                }
                <Row>
                    <Form inline className="fullwidth">
                        <Form.Group controlId="setting.QueryType">
                            <Form.Label>Quer Type</Form.Label>
                            <Form.Control as="select"
                                defaultValue={this.state.queryType}
                                onChange={element =>
                                    this.setState({ queryType: parseInt(element.currentTarget.value) })}>
                                <option value={0}>All</option>
                                <option value={1}>By Type</option>
                                <option value={2}>By Id</option>
                            </Form.Control>
                        </Form.Group>
                        {(this.queryInputs.length > 0) &&
                            this.queryInputs.map(input =>
                                input)}
                        <Form.Group controlId="setting.RecordPerPage">
                            <Form.Label>Records Per Page:</Form.Label>
                            <Form.Control as="select"
                                defaultValue={this.state.perPage}
                                onChange={element => {
                                    this.setState({ perPage: element.currentTarget.value })
                                }}>
                                <option>3</option>
                                <option>5</option>
                                <option>10</option>
                                <option>15</option>
                                <option>20</option>
                            </Form.Control>
                        </Form.Group>
                        <Button onClick={() => {
                            this.getRoutes(
                                1,
                                this.state.perPage)
                        }}>Get</Button>
                    </Form>

                </Row>
                <Row className="justify-content-md-center">
                    <Table responsive striped bordered hover variant="dark">
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>Adder Id</th>
                                <th>Route Command</th>
                                <th>Action</th>
                                <th>Ingress</th>
                                <th>Ingress Device</th>
                                <th>Egress</th>
                                <th>Egress Device</th>
                                <th>From IP</th>
                                <th>From Port</th>
                                <th>From Service Name</th>
                                <th>To IP</th>
                                <th>To Port</th>
                                <th>To Service Name</th>
                                <th>Protocol</th>
                                <th>Comment</th>
                                <th>Add Date</th>
                                <th>Manage</th>
                            </tr>
                        </thead>
                        <tbody>
                            {this.state.routes.map(route =>
                                <RouteListItem
                                    key={route.id}
                                    route={route}
                                    editRoute={this.editRoute}
                                    deleteConfirmOpener={this.deleteConfirmOpener} />)}
                        </tbody>
                    </Table>



                    <Paginator
                        activePage={this.state.activePage}
                        pages={this.state.pages}
                        handlePageChange={this.handlePageChange} />
                </Row>
                <Modal
                    show={this.state.showConfirmation}
                    onHide={this.reject}>
                    <Modal.Header closeButton>
                        <Modal.Title>Delete Route</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>{this.message}</p>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="success"
                            onClick={() =>
                                this.deleteRouteHandler(this.state.route.id)}>Yes</Button>
                        <Button
                            variant="danger"
                            onClick={this.reject}>NO</Button>
                    </Modal.Footer>
                </Modal>
                <Modal
                    show={this.state.isAddingRoute}
                    onHide={() => this.setState({ isAddingRoute: false })}>
                    <Modal.Header closeButton>
                        <Modal.Title>Add Route</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <AddRoute
                            token={this.token}
                            route={this.state.route}
                            addRouteCloser={this.addRouteCloser} />
                    </Modal.Body>
                </Modal>
                <Row className="justify-content-md-center">
                    <ListGroup
                        style={{
                            maxHeight: '200px',
                            overflowY: 'auto'
                        }}
                        scrollable={true.toString()}>
                        {
                            this.state.reports.map(report => <ListGroup.Item key={report.date}>{
                                report.result} {report.date}
                            </ListGroup.Item>)
                        }
                    </ListGroup>
                </Row>
                <Button
                    style={{
                        borderRadius: 50 + '%',
                        fontWeight: 'bolder'
                    }}
                    onClick={() => this.setState({ isAddingRoute: true })}
                >
                    +
                </Button>
            </Container >
        );
    }
};

export default RouteList;