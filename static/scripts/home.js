import React from 'react';
import { Container, Jumbotron, Row } from 'react-bootstrap';

const Home = () => {
    return (
        <Container fluid>
            <Row className="justify-content-md-center">
                <h1>UFW service manager</h1>
            </Row>
            <Row className="justify-content-md-center">
                <h4>
                    This is a web app for managing UFW service
                    </h4>
            </Row>
        </Container>

    )
};

export default Home;