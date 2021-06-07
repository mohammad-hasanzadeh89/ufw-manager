
import React, { Component } from 'react'
import DeletedRuleListItem from './deleted-rule-list-item';
import Paginator from './paginator';
import {
    Container, Row, Form,
    Button, Table, Spinner, Badge
} from 'react-bootstrap';
import baseURL from './baseURL.json';

class DeletedRuleList extends Component {
    token;
    AdderId;
    DeleterId;
    queryInputs;
    constructor(props) {
        super(props);

        this.token = props.token;
        this.isAdmin = props.isAdmin;
        this.isManager = props.isManager;
        this.AdderId = undefined;
        this.DeleterId = undefined;
        this.queryInputs = [];

        this.state = {
            isLoading: false,
            queryType: 0,
            ruleType: "allow",
            rules: [],
            rule: undefined,
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
            this.getRules(pageNumber, this.state.perPage)
        }
    }

    queryInputsHandler = () => {
        this.queryInputs = [];

        let queryInput;
        let queryInput1;
        switch (this.state.queryType) {
            case 1:
                queryInput = <Form.Group key="RuleType" controlId="setting.RuleType">
                    <Form.Label>Rule Type</Form.Label>
                    <Form.Control as="select"
                        value={this.state.ruleType}
                        onChange={element => {
                            this.setState({ ruleType: element.currentTarget.value })
                        }}>
                        <option>allow</option>
                        <option>deny</option>
                        <option>reject</option>
                        <option>limit</option>
                    </Form.Control>
                </Form.Group>
                break;
            case 2:
                queryInput = <Form.Group key="setting.AdderId" controlId="setting.AdderId">
                    <Form.Label>Adder Id</Form.Label>
                    <Form.Control placeholder="Adder Id"
                        defaultValue={this.AdderId}
                        onChange={element => {
                            this.AdderId = element.currentTarget.value
                        }} />
                </Form.Group>

                queryInput1 = <Form.Group key="setting.DeleterId" controlId="setting.DeleterId">
                    <Form.Label>Deleter Id</Form.Label>
                    <Form.Control placeholder="Deleter Id"
                        defaultValue={this.DeleterId}
                        onChange={element => {
                            this.DeleterId = element.currentTarget.value
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

    getRules = async (activePage, perPage) => {
        this.setState({ isLoading: true })
        let args = `?page=${activePage}` +
            `&perPage=${perPage}`
        let endPoint = "get_all_deleted_rules"
        switch (this.state.queryType) {
            case 1:
                args += `&ruleAction=${this.state.ruleType}`
                endPoint = "get_deleted_rules_by_type"
                break
            case 2:
                args += `&deleterUserId=${this.DeleterId}`
                args += `&adderUserId=${this.AdderId}`
                endPoint = "get_deleted_rules_by_user_id"
                break
            default:
                break
        }
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
                        rules: [],
                        rule: undefined,
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
                            rules: data.result,
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
        this.getRules(this.state.activePage, this.state.perPage)
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
                    <h1>Deleted Rules</h1>
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
                                <option value={1}>By Type</option>
                                <option value={2}>By Adder &amp; Deleter Id</option>
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
                            this.getRules(
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
                                <th>Command</th>
                                <th>Adder Id</th>
                                <th>Add Date</th>
                                <th>Deleter Id</th>
                                <th>Delete Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(this.state.rules.length > 0) && this.state.rules.map(rule =>
                                <DeletedRuleListItem
                                    key={rule.id}
                                    rule={rule} />)
                            }
                        </tbody>
                    </Table>

                    {
                        this.state.showConfirmation &&
                        <div className="confirmtion-box">
                            <p>{this.message}</p>
                            <button
                                onClick={() =>
                                    this.deleteRuleHandler(this.state.rule.id)}>Yes</button>
                            <button
                                onClick={this.reject}>NO</button>
                        </div>

                    }
                    <Paginator
                        activePage={this.state.activePage}
                        pages={this.state.pages}
                        handlePageChange={this.handlePageChange} />
                </Row>
            </Container>



        );
    }
};

export default DeletedRuleList;