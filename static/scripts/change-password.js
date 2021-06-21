import React, { Component } from 'react';
import {
    Badge, Button, Col, Container,
    Form, Row, Spinner
} from 'react-bootstrap';
import baseURL from './baseURL.json'

class ChangePassword extends Component {
    token;
    strike;
    constructor(props) {
        super(props);

        this.token = props.token;
        this.isAdmin = props.isAdmin;
        this.isManager = props.isManager;
        this.strike = 0;

        this.state = {
            isLoading: false,
            message: undefined,
            currentPassword: "",
            newPassword: "",
            confirmNewPassword: ""
        };
    };

    resetForm = () => {
        this.setState({
            currentPassword: "",
            newPassword: "",
            confirmNewPassword: ""
        })
        document.getElementById("changePasswordForm").reset();
    }

    changePassword = async e => {
        const response = await fetch(baseURL.url + 'change_password', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token
                    }`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: this.state.currentPassword,
                new_password: this.state.newPassword,
                confirm_new_password: this.state.confirmNewPassword
            })
        })
        if (!response.ok) {
            if (response.status === 401) {
                sessionStorage.clear()
                window.location.replace("/")
            }
            else if (response.status === 422) {
                sessionStorage.clear()
                window.location.replace("/")
            }
            else if (response.status === 403) {
                this.strike++;
                console.log(this.strike)
                if (this.strike >= 3) {
                    sessionStorage.clear()
                    window.location.replace("/")
                }
            }
        }

        const data = await response.json()
        this.setState({
            message: data.message,
            currentPassword: "",
            newPassword: "",
            confirmNewPassword: "",
            isLoading: false
        })

        if (response.status === 200) {
            setTimeout(() => {
                sessionStorage.clear()
                window.location.replace("/")
            }, 3000);
        }
    }
    handleChangePassword = async e => {
        e.preventDefault();
        this.setState({ isLoading: true })
        if (this.state.currentPassword !== "" &&
            this.state.newPassword !== "" &&
            this.state.confirmNewPassword !== "") {
            if (this.state.newPassword === this.state.confirmNewPassword) {
                await this.changePassword(e)
            }
            else {
                document.getElementById("changePasswordForm").reset();
                this.setState({
                    message: 'New Password and Confirm New Password is not equal!',
                    currentPassword: "",
                    newPassword: "",
                    confirmNewPassword: "",
                    isLoading: false
                })
            }
        } else {
            document.getElementById("changePasswordForm").reset();
            this.setState({
                message: 'Please enter respective value for all fields',
                currentPassword: "",
                newPassword: "",
                confirmNewPassword: "",
                isLoading: false
            })
        }

    };

    render() {
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
                    <h1>Change Password</h1>
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
                <Row className="justify-content-md-center">
                    <Form id="changePasswordForm">
                        <Form.Group controlId="changePasswordForm.CurrentPassword">
                            <Form.Label>Current Password</Form.Label>
                            <Form.Control type="password"
                                placeholder="Current Password"
                                defaultValue={this.username}
                                onChange={e => this.state.currentPassword = e.target.value}
                            />
                        </Form.Group>
                        <Form.Group controlId="changePasswordForm.Password">
                            <Form.Label>New Password</Form.Label>
                            <Form.Control type="password"
                                placeholder="New Password"
                                defaultValue={this.state.newPassword}
                                onChange={e => this.state.newPassword = e.target.value} />
                        </Form.Group>
                        <Form.Group controlId="changePasswordForm.ConfirmPassword">
                            <Form.Label>Confirm New Password</Form.Label>
                            <Form.Control type="password"
                                placeholder="Confirm New Password"
                                defaultValue={this.state.confirmNewPassword}
                                onChange={e => this.state.confirmNewPassword = e.target.value} />
                        </Form.Group>
                        <Row className="fullwidth">
                            <Col>
                                <Button variant="success"
                                    type="submit"
                                    onClick={this.handleChangePassword}>
                                    submit
                                </Button>
                            </Col>
                            <Col>
                                <Button variant="danger"
                                    type="reset"
                                    onClick={this.resetForm}>
                                    Reset
                                </Button>
                            </Col>
                        </Row>
                    </Form>
                </Row>
            </Container>
        )
    };
}

export default ChangePassword;