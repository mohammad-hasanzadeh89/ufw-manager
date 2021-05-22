

import React, { Component } from 'react'

class StatusListItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            status: props.status
        }
    }

    cleanRuleFromNull = (obj) => {
        let temp = {}

        let keys = Object.keys(obj);
        for (let i = 0; i < keys.length; i++) {
            let key = keys[i]
            let val = obj[key]
            if (val === null)
                val = "null"
            temp[key] = val
        }
        return temp
    }

    render() {
        const status = this.cleanRuleFromNull(this.state.status)
        return (
            <tr>
                <td>{status.id.toString()}</td>
                <td>{status.user_id.toString()}</td>
                <td>{status.ufw_status ? "enabled" : "disabled"}</td>
                <td>{status.change_date}</td>
            </tr>

        );
    }

};

export default StatusListItem;
