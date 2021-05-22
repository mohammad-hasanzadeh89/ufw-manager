import React, { Component } from 'react';
import { Container, Row, Col, Form, Button, Table, Badge } from 'react-bootstrap';
import baseURL from './baseURL.json';



const signupUser = async (_username, _password, _confirmPassword) => {
    if (_username && _password && _confirmPassword) {
        if (_password.normalize() === _confirmPassword.normalize()) {
            return fetch(baseURL.url + 'signup', {
                method: 'POST',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: _username, password: _password })
            }).then(data => data.json());
        } else {
            return { message: `Password and confirm password is not equal!` }
        }
    } else {
        return { message: `Please enter respective value for all fields` }
    }
};

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
    username;
    password;
    confirmPassword;
    constructor(props) {
        super(props);
        this.setToken = props.setToken
        this.setIsAdmin = props.setIsAdmin
        this.setIsManager = props.setIsManager
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
        this.confirmPassword = "";
    }

    formSwitcher = () => {
        let temp = !this.state.isNewUser
        let title = temp ? "Sign Up" : "Sign In";
        let signupOrSigninMsg = temp ? "Sign In instead" : "Create an account";
        this.resetForm()
        this.setState({
            isNewUser: temp,
            title: title,
            signupOrSigninMsg: signupOrSigninMsg
        });
    }

    handleGetgUserPrivileges = async (token) => {
        const data = await getgUserPrivileges(token)
        if (data.result.isAdmin !== undefined && data.result.isManager !== undefined) {
            this.setIsAdmin(data.result.isAdmin);
            this.setIsManager(data.result.isManager);
        } else {
            this.setState({ message: data.result })
        }
    }

    handleSigninSubmit = async e => {
        e.preventDefault();
        const data = await signinUser(
            this.username,
            this.password
        )
        if (data.access_token) {
            await this.handleGetgUserPrivileges(data.access_token)
            this.setToken(data.access_token);
        } else {
            this.setState({ message: data.message })
        }
    };

    handleSignupSubmit = async e => {
        e.preventDefault();
        const data = await signupUser(
            this.username,
            this.password,
            this.confirmPassword
        )
        if (data.message) {
            this.setState({ message: data.message })
        } else {
            this.setState({ message: "something went wrong!" })
        }
    };

    render() {
        return (
            <div className="auth-wrapper" >

                <Container fluid>
                    <Row className="justify-content-md-center">
                        <h1>{this.state.title}</h1>
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
                    {
                        !this.state.isNewUser ?
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
                                                {this.state.title}
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
                            :
                            <Row className="justify-content-md-center">
                                <Form
                                    onSubmit={this.handleSignupSubmit}>
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
                                    <Form.Group controlId="signinForm.ConfirmPassword">
                                        <Form.Label>Confirm Password</Form.Label>
                                        <Form.Control type="password"
                                            placeholder="Confirm Password"
                                            defaultValue={this.confirmPassword}
                                            onChange={e => this.confirmPassword = e.target.value} />
                                    </Form.Group>
                                    <Row className="fullwidth">
                                        <Col>
                                            <Button variant="success"
                                                type="submit">
                                                {this.state.title}
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
                    }
                    <Row className="justify-content-md-center fullwidth">
                        <Button
                            id="signupOrSignin"
                            variant="primary"
                            onClick={this.formSwitcher}>
                            {this.state.signupOrSigninMsg}
                        </Button>
                    </Row>

                </Container>
            </div >
        );
    };
}

export default Auth;