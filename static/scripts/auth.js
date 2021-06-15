import React, { Component } from 'react';
import { Container, Row, Col, Form, Button, Table, Badge } from 'react-bootstrap';
import baseURL from './baseURL.json';

const signinUser = async (_username, _password) => {
    if (_username && _password) {
        return fetch(baseURL.url + 'signin', {
            method: 'POST',
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: _username, password: _password })
        }).then(data => data.json());
    } else {
        return { message: "Please enter username and password" }
    }

};

const getgUserPrivileges = async (token) => {
    return fetch(baseURL.url + 'get_user_privileges', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
    }).then(data => data.json());
};

class Auth extends Component {
    setToken;
    setIsAdmin;
    setIsManager;
    setIsFirst;
    username;
    password;
    constructor(props) {
        super(props);
        this.setToken = props.setToken;
        this.setIsAdmin = props.setIsAdmin;
        this.setIsManager = props.setIsManager;
        this.setIsFirst = props.setIsFirst;

        this.state = {
            token: null,
            isLoading: false,
            title: "Sign In",
            signupOrSigninMsg: "Create an account",
            message: undefined
        }
    }

    resetForm = () => {
        this.username = "";
        this.password = "";
    }

    handleSigninSubmit = async e => {
        e.preventDefault();
        const data = await signinUser(
            this.username,
            this.password
        )
        if (data.access_token) {
            this.setToken(data.access_token);
            this.setIsAdmin(data.user.admin_privileges);
            this.setIsManager(data.user.manager_privileges);
            this.setIsFirst(data.user.is_first);
        } else {
            this.setState({ message: data.message })
        }
    };

    render() {
        return (
            <div className="auth-wrapper" >
                <Container fluid>
                    <Row className="justify-content-md-center">
                        <h1>Sign In</h1>
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
                        <Form
                            onSubmit={this.handleSigninSubmit}>
                            <Form.Group controlId="signinForm.Username">
                                <Form.Label>User Name</Form.Label>
                                <Form.Control type="text"
                                    placeholder="User Name"
                                    defaultValue={this.username}
                                    onChange={e => this.username = e.target.value}
                                />
                            </Form.Group>
                            <Form.Group controlId="signinForm.Password">
                                <Form.Label>Password</Form.Label>
                                <Form.Control type="password"
                                    placeholder="Password"
                                    defaultValue={this.password}
                                    onChange={e => this.password = e.target.value} />
                            </Form.Group>
                            <Row className="fullwidth">
                                <Col>
                                    <Button variant="success"
                                        type="submit">
                                        Sign In
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
            </div >
        );
    };
}

export default Auth;