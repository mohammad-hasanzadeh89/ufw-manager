import React, { Component } from 'react'
import { Button } from 'react-bootstrap';

class UserListItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: props.user,
            grantAuthOpener: props.grantAuthOpener
        }
    }
    render() {
        const user = this.state.user
        return (
            <tr>
                <td>{user.id.toString()}</td>
                <td>{user.username}</td>
                <td>{user.manager_privileges.toString()}</td>
                <td>{!user.manager_privileges &&
                    <Button
                        variant="warning"
                        onClick={
                            () => { this.state.grantAuthOpener(user) }}
                        aria-controls="confirm-box"
                        aria-expanded={this.props.isEditing}>
                        Grant Manager Authorization
                    </Button>
                }</td>
            </tr>
        );
    }

};

export default UserListItem;