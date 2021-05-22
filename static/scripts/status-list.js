
import React, { Component } from 'react'
import StatusListItem from './status-list-item';
import Paginator from './paginator';
import {
    Container, Row, Form,
    Button, Table, Spinner, Badge
} from 'react-bootstrap';
import baseURL from './baseURL.json';


class StatusList extends Component {
    token;
    queryInputs;
    constructor(props) {
        super(props);

        this.token = props.token;
        this.isAdmin = props.isAdmin;
        this.isManager = props.isManager;
        this.queryInputs = [];

        this.state = {
            isLoading: false,
            queryType: 0,
            changerId: undefined,
            from_date: undefined,
            to_date: undefined,
            statuses: [],
            status: undefined,
            message: undefined,
            activePage: 1,
            total: 0,
            pages: 0,
            perPage: 5
        };

    };

    handlePageChange = (pageNumber) => {
        if (pageNumber > 0 && pageNumber <= this.state.pages &&
            pageNumber !== this.state.activePage) {
            this.getStatus(pageNumber, this.state.perPage)
        }
    }

    queryInputsHandler = () => {
        this.queryInputs = [];

        let queryInput;
        let queryInput1;
        switch (this.state.queryType) {
            case 1:
                queryInput = <Form.Group
                    key="from_datePicker"
                    controlId="from_datePicker"
                >

                    <Form.Label>From Date:</Form.Label>

                    <Form.Control
                        type="date"
                        name="from_datePicker"
                        onChange={element => {
                            this.setState({
                                from_date: element.currentTarget.value
                            }, () => console.log(this.state.from_date))
                        }}
                        defaultValue={this.state.from_date} />

                </Form.Group>
                queryInput1 = <Form.Group
                    key="to_datePicker"
                    controlId="to_datePicker"
                >

                    <Form.Label>To Date:</Form.Label>

                    <Form.Control
                        type="date"
                        name="to_datePicker"
                        onChange={element => {
                            this.setState({
                                to_date: element.currentTarget.value
                            }, () => console.log(this.state.to_date))
                        }}
                        defaultValue={this.state.to_date} />

                </Form.Group>
                break;
            case 2:
                queryInput = <Form.Group key="setting.changerId" controlId="setting.changerId">
                    <Form.Label>User Id</Form.Label>
                    <Form.Control placeholder="User Id"
                        defaultValue={this.state.changerId}
                        type="number"
                        onChange={element => {
                            this.setState({
                                changerId: element.currentTarget.value
                            })
                        }} />
                </Form.Group>
                break;
            default:
                break
        }
        if (queryInput !== undefined) {
            this.queryInputs.push(queryInput)
        }
        if (queryInput1 !== undefined) {
            this.queryInputs.push(queryInput1)
        }
    }

    getStatus = async (activePage, perPage) => {
        this.setState({ isLoading: true })
        let args = `?page=${activePage}` +
            `&perPage=${perPage}`
        let endPoint = "get_status_change_records_by_user_id"
        switch (this.state.queryType) {
            case 1:
                if (this.state.from_date) {
                    args += `&from_date=${this.state.from_date} 00:00:00`
                }
                if (this.state.to_date) {
                    args += `&to_date=${this.state.to_date} 23:59:59`
                }
                endPoint = "get_status_change_records_by_time"
                break
            case 2:
                args += `&userId=${this.state.changerId}`
                break
            default:
                break
        }
        console.log(this.state.from_date)
        console.log(this.state.to_date)
        console.log(args)
        fetch(
            baseURL.url + endPoint + args, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.token
                    }`,
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
                    let alertMsg = response.status.toString()
                    alertMsg += " " + response.statusText

                    this.setState({
                        isLoading: false,
                        statuses: [],
                        status: undefined,
                        message: alertMsg,
                        activePage: 1,
                        total: 0,
                        pages: 0
                    })
                    return undefined
                }
            }).then(
                data => {
                    if (data) {
                        this.setState({
                            statuses: data.result,
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
        this.getStatus(this.state.activePage, this.state.perPage)
    }

    render() {
        if (!this.isAdmin) {
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
                    <h1>Status Change Records</h1>
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
                                value={this.state.queryType}
                                onChange={element =>
                                    this.setState({ queryType: parseInt(element.currentTarget.value) })}>
                                <option value={0}>All</option>
                                <option value={1}>By Date</option>
                                <option value={2}>By User Id</option>
                            </Form.Control>
                        </Form.Group>
                        {(this.queryInputs.length > 0) &&
                            this.queryInputs.map(input =>
                                input)}
                        <Form.Group controlId="setting.RecordPerPage">
                            <Form.Label>Records Per Page:</Form.Label>
                            <Form.Control as="select"
                                value={this.state.perPage}
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
                            this.getStatus(
                                1,
                                this.state.perPage)
                        }}>Get</Button>
                    </Form>

                </Row>
                <Row className="justify-content-md-center">
                    <Table striped bordered hover variant="dark">
                        <thead>
                            <tr>
                                <th>Id</th>
                                <th>User Id</th>
                                <th>UFW Status</th>
                                <th>Change Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(this.state.statuses.length > 0) && this.state.statuses.map(status =>
                                <StatusListItem
                                    key={status.id}
                                    status={status} />)
                            }
                        </tbody>
                    </Table>

                    <Paginator
                        activePage={this.state.activePage}
                        pages={this.state.pages}
                        handlePageChange={this.handlePageChange} />
                </Row>
            </Container>



        );
    }
};

export default StatusList;