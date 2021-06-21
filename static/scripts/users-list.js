import React, { Component } from 'react'
import UserListItem from './users-list-item';
import {
    Container, Row, Table, Modal,
    Form, Button, Badge, Spinner
} from 'react-bootstrap';
import Paginator from './paginator';
import baseURL from './baseURL.json';

class UsersList extends Component {
    token;
    isAdmin;
    isManager;
    queryId;
    queryUsername;

    constructor(props) {
        super(props);

        this.token = props.token;
        this.isAdmin = props.isAdmin;
        this.isManager = props.isManager;
        this.queryId = undefined;
        this.queryUsername = undefined;

        this.state = {
            users: [],
            isLoading: false,
            isEditing: false,
            isDeleting: false,
            isAddingNewUser: false,
            message: undefined,
            user: undefined,
            username: "",
            password: "",
            confirmPassword: "",
            activePage: 1,
            total: 0,
            pages: 0,
            perPage: 5
        }
    }

    grantAuthOpener = (user) => {
        this.setState({
            isEditing: true,
            user: user,
            username: user.username
        })
    }

    deleteUserOpener = (user) => {
        this.setState({
            isDeleting: true,
            user: user,
            username: user.username
        })
    }

    reject = () => {
        this.setState({
            isEditing: false,
            isDeleting: false,
            user: undefined
        })
    }

    grantAuthHandler = () => {
        this.setState({ isLoading: true })
        fetch(baseURL.url + 'grant_authorization', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: this.state.username })
        }).then(response => {
            if (response.ok) {
                return response.json()
            } else {
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
                console.log(response)
                let alertMsg = response.status.toString()
                alertMsg += " " + response.statusText
                this.setState({
                    isLoading: false,
                    users: [],
                    user: undefined,
                    message: alertMsg,
                    username: "",
                    activePage: 1,
                    total: 0,
                    pages: 0,
                })
                return undefined
            }
        }).catch(error => {
            let alertMsg = error.toString()

            this.setState({
                isLoading: false,
                users: [],
                user: undefined,
                message: alertMsg,
                username: "",
                activePage: 1,
                total: 0,
                pages: 0,
            })
        }).then(
            data => {
                this.setState({
                    isEditing: false,
                    isLoading: false,
                    user: undefined,
                    message: data.message
                })
                this.componentDidMount()
            });
    }

    deleteUserHandler = () => {
        this.setState({ isLoading: true })
        fetch(baseURL.url + 'delete_user', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: this.state.username })
        }).then(response => {
            if (response.ok) {
                return response.json()
            } else {
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
                let alertMsg = response.status.toString()
                alertMsg += " " + response.statusText
                this.setState({
                    isLoading: false,
                    users: [],
                    user: undefined,
                    message: alertMsg,
                    username: "",
                    activePage: 1,
                    total: 0,
                    pages: 0,
                })
                return undefined
            }
        }).catch(error => {
            let alertMsg = error.toString()

            this.setState({
                isLoading: false,
                users: [],
                user: undefined,
                message: alertMsg,
                username: "",
                activePage: 1,
                total: 0,
                pages: 0,
            })
            return undefined
        }).then(
            data => {
                if(typeof(data) !== 'undefined') {
                this.setState({
                    isDeleting: false,
                    isLoading: false,
                    user: undefined,
                    message: data.message
                })
                this.componentDidMount()
            }
            });
    }

    handlePageChange = (pageNumber) => {
        if (pageNumber > 0 && pageNumber <= this.state.pages &&
            pageNumber !== this.state.activePage) {
            this.getUsers(pageNumber, this.state.perPage)
        }
    }

    getUsers = async (activePage, perPage) => {
        this.setState({ isLoading: true })
        let args = `?page=${activePage}` +
            `&perPage=${perPage}`
        let endPoint;
        if (!this.queryId && !this.queryUsername) {
            endPoint = 'get_all_user'
        } else {
            if (this.queryId)
                args += `&id=${this.queryId}`
            if (this.queryUsername)
                args += `&username=${this.queryUsername}`
            endPoint = 'get_users'
        }

        fetch(baseURL.url + endPoint + args, {
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
                    console.log(response)
                    let alertMsg = response.status.toString()
                    alertMsg += " " + response.statusText
                    this.setState({
                        isLoading: false,
                        users: [],
                        user: undefined,
                        message: alertMsg,
                        username: "",
                        activePage: 1,
                        total: 0,
                        pages: 0,
                    })
                    return undefined
                }
            }).catch(error => {
                let alertMsg = error.toString()

                this.setState({
                    isLoading: false,
                    users: [],
                    user: undefined,
                    message: alertMsg,
                    username: "",
                    activePage: 1,
                    total: 0,
                    pages: 0,
                })
            }).then(
                data => {
                    if(typeof(data) !== 'undefined') {
                        this.setState({
                            message: undefined,
                            users: data.result,
                            activePage: activePage,
                            total: data.total,
                            pages: Math.ceil(data.total / this.state.perPage),
                            perPage: perPage,
                            isLoading: false
                        })
                    }  
                });
    }

    addUser = () => {
        if (this.state.username.length >= 4 && this.state.password.length >= 8 && this.state.confirmPassword.length >= 8) {
            if (this.state.password.normalize() === this.state.confirmPassword.normalize()) {
                return fetch(baseURL.url + 'add_user', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username: this.state.username, password: this.state.password })
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
                    }).catch(error => {
                    let alertMsg = error.toString()

                    this.setState({
                        isLoading: false,
                        users: [],
                        user: undefined,
                        message: alertMsg,
                        username: "",
                        activePage: 1,
                        total: 0,
                        pages: 0,
                    })
                    return undefined
                }).then(data => {
                    if (typeof(data) !== 'undefined' &&
                         data.message) {
                        this.setState({
                            message: data.message,
                            isAddingNewUser: false,
                            username: "",
                            password: "",
                            confirmPassword: ""
                        }, () =>
                            this.getUsers(this.state.activePage, this.state.perPage))
                    } else {
                        this.setState({ message: "something went wrong!" })
                    }
                });
            } else {
                return { message: `Password and confirm password is not equal!` }
            }
        } else {
            this.setState({ message: `Please enter respective value for all fields` })
        }
    };

    onHideAddNewUser = () => {
        this.setState({
            isAddingNewUser: false,
            message: undefined
        })
    }

    resetForm = () => {
        document.getElementById('addUserForm').reset()
        this.setState({
            message: undefined,
            username: "",
            password: "",
            confirmPassword: "",
        });
    }

    componentDidMount() {
        this.getUsers(this.state.activePage, this.state.perPage)
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
        return (
            <Container fluid>
                <Row className="justify-content-md-center">
                    <h1>Users</h1>
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
                    <Form inline className="fullwidth">
                        <Form.Group key="ids" controlId="setting.Id">
                            <Form.Label>Id:</Form.Label>
                            <Form.Control placeholder="User Id"
                                defaultValue={this.queryId}
                                onChange={element => {
                                    this.queryId = element.currentTarget.value
                                }} />
                        </Form.Group>

                        <Form.Group controlId="setting.Username">
                            <Form.Label>User Name</Form.Label>
                            <Form.Control placeholder="User Name"
                                defaultValue={this.queryUsername}
                                onChange={element => {
                                    this.queryUsername = element.currentTarget.value
                                }} />
                        </Form.Group>
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
                            this.getUsers(
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
                                <th>User Name</th>
                                <th>Manager Privileges</th>
                                <th>Is Deleted</th>
                                <th>Manage</th>
                            </tr>
                        </thead>
                        <tbody>
                            {this.state.users.map(user =>
                                <UserListItem
                                    key={user.id}
                                    user={user}
                                    grantAuthOpener={this.grantAuthOpener}
                                    deleteUserOpener={this.deleteUserOpener}
                                    isEditing={this.isEditing} />
                            )}
                        </tbody>
                    </Table>
                    <Paginator
                        activePage={this.state.activePage}
                        pages={this.state.pages}
                        handlePageChange={this.handlePageChange} />
                </Row>
                <Modal show={this.state.isEditing}
                    onHide={this.reject}>
                    <Modal.Header closeButton>
                        <Modal.Title>Authorizate User</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>
                            Are you sure, You want to grant manager
                            privileges to {this.state.username} ?
                        </p>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="success"
                            onClick={() =>
                                this.grantAuthHandler()}>Yes</Button>
                        <Button
                            variant="danger"
                            onClick={this.reject}>NO</Button>
                    </Modal.Footer>
                </Modal>
                <Modal show={this.state.isDeleting}
                    onHide={this.reject}>
                    <Modal.Header closeButton>
                        <Modal.Title>Delete User</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>
                            Are you sure, You want to
                            delete user with this
                            username '{this.state.username}' ?
                        </p>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="success"
                            onClick={() =>
                                this.deleteUserHandler()}>Yes</Button>
                        <Button
                            variant="danger"
                            onClick={this.reject}>NO</Button>
                    </Modal.Footer>
                </Modal>

                <Modal show={this.state.isAddingNewUser}
                    onHide={this.onHideAddNewUser}>
                    <Modal.Header closeButton>
                        <Modal.Title>Add New User</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
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
                        <Form id="addUserForm" noValidate>
                            <Form.Group controlId="addUserForm.Username">
                                <Form.Label>User Name</Form.Label>
                                <Form.Control type="text"
                                    placeholder="Username"
                                    value={this.state.username}
                                    onChange={e => this.setState({ username: e.target.value })}
                                />
                                <Form.Text id="usernameHelpBlock" muted>the minimum username length  is 4 character</Form.Text>
                            </Form.Group>
                            <Form.Group controlId="addUserForm.Password">
                                <Form.Label>Password</Form.Label>
                                <Form.Control type="password"
                                    placeholder="Password"
                                    value={this.state.password}
                                    onChange={e => this.setState({ password: e.target.value })} />
                                <Form.Text id="passwordHelpBlock" muted>password must contin at least 8 character and must be used lower-case and upper-case letter and digit and symbols like Test123!</Form.Text>
                            </Form.Group>
                            <Form.Group controlId="addUserForm.ConfirmPassword">
                                <Form.Label>Confirm Password</Form.Label>
                                <Form.Control type="password"
                                    placeholder="Confirm Password"
                                    value={this.state.confirmPassword}
                                    onChange={e => this.setState({ confirmPassword: e.target.value })} />
                            </Form.Group>
                        </Form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="success"
                            onClick={this.addUser}>
                            Add User
                        </Button>
                        <Button variant="danger"
                            onClick={this.resetForm}>
                            Reset
                        </Button>
                    </Modal.Footer>
                </Modal>
                <Button
                    style={{
                        borderRadius: 50 + '%',
                        fontWeight: 'bolder'
                    }}
                    onClick={() => this.setState({
                        isAddingNewUser: true,
                        username: "",
                        message: undefined
                    })}
                >
                    +
                </Button>
            </Container >
        );
    }

};

export default UsersList;