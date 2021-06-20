import React, { Component } from 'react'
import { Button } from 'react-bootstrap';

class UserListItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: props.user,
            grantAuthOpener: props.grantAuthOpener,
            deleteUserOpener: props.deleteUserOpener
        }
    }
    render() {
        const user = this.state.user
        return (
            <tr>
                <td>{user.id.toString()}</td>
                <td>{user.username}</td>
                <td>{user.manager_privileges.toString()}</td>
                <td>{user.is_deleted.toString()}</td>
                <td>{(!user.manager_privileges &&
                    !user.is_deleted) &&
                    <Button
                        style={{ marginRight: '1rem' }}
                        variant="warning"
                        onClick={
                            () => { this.state.grantAuthOpener(user) }}
                        aria-controls="confirm-box"
                        aria-expanded={this.props.isEditing}>
                        Grant Manager Authorization
                    </Button>
                }
                    {!user.is_deleted &&
                        <Button
                            variant="danger"
                            onClick={
                                () => { this.state.deleteUserOpener(user) }}
                            aria-controls="confirm-box"
                            aria-expanded={this.props.isEditing}>
                            Delete User
                        </Button>
                    }</td>
            </tr>
        );
    }

};

export default UserListItem;