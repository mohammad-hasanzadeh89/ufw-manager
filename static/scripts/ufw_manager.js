import React, { Component } from 'react';
import {
    Container, Button, Row, ListGroup,
    Modal, Spinner, Image
} from 'react-bootstrap';
import baseURL from './baseURL.json'
import disablePic from '../img/disable.png'
import enablePic from '../img/enable.png'
class UFWManager extends Component {

    token;
    message;
    nextAction;
    reports;

    constructor(props) {
        super(props);
        this.token = props.token;
        this.isAdmin = props.isAdmin;
        this.isManager = props.isManager;
        this.strikes = props.strikes;
        this.message = ""

        this.nextAction = undefined
        this.state = {
            isLoading: false,
            reports: [],
            isEnable: false,
            status: { result: [], date: "" },
            isCheckingStatus: false,
            showConfirmation: false,
            warning: false
        }
    };
    statusWithDetail = () => {
        this.getStatus();
        this.setState({
            isCheckingStatus: true
        })
    }

    closeStatus = () => {
        this.setState({
            isCheckingStatus: false
        })
    }

    showConfirmMessage = (nextAction) => {
        this.message =
            `Are you sure you want to ${nextAction} UFW service?`;
        if (nextAction == "reset") {
            this.setState({ warning: true })
        } else {
            this.setState({ warning: false })
        }
        this.nextAction = nextAction;
        this.setState({ showConfirmation: true })
    }

    confirm = () => {
        this.setState({ showConfirmation: false })
        this.manageUFW(this.nextAction);
    }

    reject = () => {
        this.setState({ showConfirmation: false })
    }

    manageUFW = async (action) => {
        this.setState({ isLoading: true })
        const response = await fetch(baseURL.url + action, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.token
                    }`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        })
        const data = await response.json()
        if (response.ok) {
            let status = false
            if (!data.result.includes("disabled") ||
                !data.result.includes("not enabled")) {
                if (action === "enable" ||
                    action === "realod") {
                    status = true
                }
            }
            this.state.reports.unshift(data)
            this.setState({
                isLoading: false,
                isEnable: status,
                reports: this.state.reports
            });
        } else {
            console.log(response)
            this.state.reports.unshift(data)
            this.setState({
                isLoading: false,
                isEnable: false,
                reports: this.state.reports
            });
        }
        // fetch(baseURL.url + action, {
        //     method: 'GET',
        //     headers: {
        //         'Authorization': `Bearer ${this.token
        //             }`,
        //         'Access-Control-Allow-Origin': '*',
        //         'Content-Type': 'application/json'
        //     }
        // }).then(
        //     response => response.json()).catch(err => { console.log(err) }).then(
        //         data => {
        //             let status = false
        //             if (!data.result.includes("disabled") ||
        //                 !data.result.includes("not enabled")) {
        //                 if (action === "enable" ||
        //                     action === "realod") {
        //                     status = true
        //                 }
        //             }
        //             this.state.reports.unshift(data)
        //             this.setState({
        //                 isLoading: false,
        //                 isEnable: status,
        //                 reports: this.state.reports
        //             })
        //         });
    }

    getStatus = async () => {
        fetch(baseURL.url + "status", {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.token
                    }`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        }).then(
            response => response.json()).then(
                data => {
                    if (data.result[0].startsWith("Status: active")) {
                        this.setState({
                            isEnable: true,
                            status: data
                        })
                    } else {
                        this.setState({
                            isEnable: false,
                            status: data
                        })
                    }
                });
    }

    componentDidMount = () => {
        this.getStatus()
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
        return (
            <Container fluid>
                <Row className="justify-content-md-center">
                    <h2>UFWManager</h2>
                </Row>
                <Row className="justify-content-md-center">
                    <Image
                        width={125}
                        height={125}
                        src={this.state.isEnable ? enablePic : disablePic}
                        alt="disable" rounded />

                </Row>
                <Row className="justify-content-md-center">
                    <p>
                        UFW service is {this.state.isEnable ? "enable" : "disable"}
                    </p>
                </Row>
                <Row className="justify-content-md-center">
                    <h4>
                        You can manage UFW service here
                    </h4>
                </Row>
                <Row className="justify-content-md-center buttons-box-wrapper">
                    <Button
                        variant="secondary"
                        onClick={
                            () => this.showConfirmMessage("update_rules")}
                        aria-controls="confirm-box"
                        aria-expanded={this.state.showConfirmation}>
                        Update UFW<br /> Manual Changes</Button>
                    <Button
                        variant="primary"
                        onClick={
                            () => this.statusWithDetail()}
                        aria-controls="confirm-box"
                        aria-expanded={this.state.showConfirmation}>
                        UFW Status</Button>
                    <Button
                        variant="success"
                        onClick={
                            () => this.showConfirmMessage("enable")}
                        aria-controls="confirm-box"
                        aria-expanded={this.state.showConfirmation}>
                        Enable UFW</Button>
                    <Button
                        variant="warning"
                        onClick={
                            () => this.showConfirmMessage("reload")}
                        aria-controls="confirm-box"
                        aria-expanded={this.state.showConfirmation}>
                        Reload UFW</Button>
                    <Button
                        variant="danger"
                        onClick={
                            () => this.showConfirmMessage("disable")}
                        aria-controls="confirm-box"
                        aria-expanded={this.state.showConfirmation}>
                        Disable UFW</Button>
                    <Button
                        variant="dark"
                        onClick={
                            () => this.showConfirmMessage("reset")}
                        aria-controls="confirm-box"
                        aria-expanded={this.state.showConfirmation}>
                        Reset UFW</Button>
                </Row>

                <Modal
                    show={this.state.isCheckingStatus}
                    onHide={this.closeStatus}>
                    <Modal.Header closeButton>
                        <Modal.Title>Confirm</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <ListGroup
                            style={{
                                maxHeight: '200px',

                                overflowY: 'auto'
                            }}
                            scrollable={true.toString()}>
                            {
                                this.state.status.result.map(
                                    line => <ListGroup.Item
                                        key={this.state.status.result.indexOf(line)}>
                                        {line}
                                    </ListGroup.Item>)
                            }
                            <ListGroup.Item
                                key={this.state.status.date}>
                                {this.state.status.date}
                            </ListGroup.Item>
                        </ListGroup>
                        <p>{this.state.status[0]}</p>
                        <p>{this.state.status[1]}</p>
                    </Modal.Body>
                </Modal>

                <Modal
                    show={this.state.showConfirmation}
                    onHide={this.reject}>
                    <Modal.Header closeButton>
                        <Modal.Title>Confirm</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>{this.message}</p>
                        {this.state.warning &&
                            <b style={{
                                color: "red"
                            }}>
                                Warning: use this with extra caution.
                                because all rules/routes will be deleted,
                                and UFW service will be disabled
                            </b>
                        }
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="success"
                            onClick={this.confirm}>Yes</Button>
                        <Button
                            variant="danger"
                            onClick={this.reject}>NO</Button>
                    </Modal.Footer>
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
            </Container >

        )
    };

};

export default UFWManager;