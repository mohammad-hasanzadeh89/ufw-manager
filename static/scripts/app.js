import React, { Component } from 'react';
import { Navbar, Button, Nav, Container } from 'react-bootstrap';
import { hot } from 'react-hot-loader';
import { Link, Redirect, Route, Switch } from 'react-router-dom';
import jwt_decode from 'jwt-decode';
import Home from './home';
import Auth from './auth';
import UFWManager from './ufw_manager';
import '../css/app.css';
import UsersList from './users-list';
import ChangePassword from './change-password';
import RuleList from './rule-list';
import DeletedRuleList from './deleted-rule-list';
import RouteList from './route-list';
import DeletedRouteList from './deleted-route-list';
import 'bootstrap/dist/css/bootstrap.min.css';
import StatusList from './status-list';



class App extends Component {
    constructor(props) {
        super(props);

        this.state = {
            token: this.getToken(),
            isLoading: false,
            isAdmin: this.getIsAdmin(),
            isManager: this.getIsManager(),
            isFirst: this.getIsFirst()
        }
    }

    Signout = () => {
        sessionStorage.clear()
        window.location.replace("/")
    }

    setToken = (token) => {
        sessionStorage.setItem('token', JSON.stringify(token));
        this.setState({ token: token })
    }

    getToken = () => {
        const tokenString = sessionStorage.getItem('token');
        const token = JSON.parse(tokenString);
        if (token) {
            const decoded = jwt_decode(token);
            if (decoded.exp < Date.now()) {
                return token
            } else {
                return null
            }
        } else {
            return null
        }
    }

    setIsAdmin = (isAdmin) => {
        sessionStorage.setItem('isAdmin', JSON.stringify(isAdmin));
        this.setState({ isAdmin: isAdmin })

    }

    getIsAdmin = () => {
        const isAdminString = sessionStorage.getItem('isAdmin');
        const isAdmin = JSON.parse(isAdminString);
        return isAdmin
    }

    setIsManager = (isManager) => {
        sessionStorage.setItem('isManager', JSON.stringify(isManager));
        this.setState({ isManager: isManager })
    }

    getIsManager = () => {
        const isManagerString = sessionStorage.getItem('isManager');
        const isManager = JSON.parse(isManagerString);
        return isManager
    }

    setIsFirst = (isFirst) => {
        sessionStorage.setItem('isFirst', JSON.stringify(isFirst));
        this.setState({ isFirst: isFirst })
    }

    getIsFirst = () => {
        const isFirstString = sessionStorage.getItem('isFirst');
        const isFirst = JSON.parse(isFirstString);
        return isFirst
    }
    render() {
        let token = this.state.token
        if (!this.state.token) {
            return <Auth
                setToken={this.setToken}
                setIsAdmin={this.setIsAdmin}
                setIsManager={this.setIsManager}
                setIsFirst={this.setIsFirst} />
        } else {
            token = this.state.token
        }
        return (
            <div className="App wrapper">
                <Navbar collapseOnSelect expand="lg"
                    bg="dark" variant="dark">
                    <Navbar.Brand href="#home">UFW Manager</Navbar.Brand>
                    <Navbar.Toggle aria-controls="responsive-navbar-nav" />
                    <Navbar.Collapse id="responsive-navbar-nav">
                        <Nav className="mr-auto">
                            <Nav.Link href="/#home">Home</Nav.Link>
                            {
                                (this.state.isManager && !this.state.isFirst) &&
                                <Nav.Link href="#UFWManager">
                                    UFWManager
                                </Nav.Link>
                            }
                            {
                                (this.state.isManager && !this.state.isFirst) &&
                                <Nav.Link href="#rules">
                                    Rules
                                </Nav.Link>
                            }
                            {
                                (this.state.isManager && !this.state.isFirst) &&
                                <Nav.Link href="#routes">
                                    Routes
                                </Nav.Link>
                            }
                            {
                                (this.state.isAdmin && !this.state.isFirst) &&

                                <Nav.Link href="#deletedRules">
                                    Deleted Rules
                                </Nav.Link>
                            }
                            {
                                (this.state.isAdmin && !this.state.isFirst) &&

                                <Nav.Link href="#deletedRoutes">
                                    Deleted Routes
                                </Nav.Link>
                            }
                            {
                                (this.state.isAdmin && !this.state.isFirst) &&

                                <Nav.Link href="#statusChangeRecords">
                                    Status Change Records
                                </Nav.Link>
                            }
                            {
                                (this.state.isAdmin && !this.state.isFirst) &&

                                <Nav.Link href="#users">
                                    Users
                                </Nav.Link>
                            }
                            <Nav.Link href="#changePassword">
                                Change Password
                            </Nav.Link>
                        </Nav>
                        <Button variant="danger" onClick={this.Signout}>
                            sign out
                        </Button>
                    </Navbar.Collapse>
                </Navbar>

                <Container fluid>
                    <Route exact path="/">
                        <Redirect to="/home" />
                    </Route>
                    <Switch>
                        <Route path="/home">
                            <Home />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/UFWManager">
                            <UFWManager
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/users">
                            <UsersList
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/rules">
                            <RuleList
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/routes">
                            <RouteList
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/deletedRules">
                            <DeletedRuleList
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/deletedRoutes">
                            <DeletedRouteList
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/statusChangeRecords">
                            <StatusList
                                token={token}
                                isAdmin={this.state.isAdmin}
                                isManager={this.state.isManager} />
                        </Route>
                    </Switch>
                    <Switch>
                        <Route path="/changePassword">
                            <ChangePassword token={token} />
                        </Route>
                    </Switch>
                </Container>

            </div>
        );
    };
}

export default hot(module)(App);