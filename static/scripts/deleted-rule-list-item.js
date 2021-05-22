import React, { Component } from 'react'

class DeletedRuleListItem extends Component {
    constructor(props) {
        super(props);
        this.state = {
            rule: props.rule
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
        const rule = this.cleanRuleFromNull(this.state.rule)
        return (
            <tr>
                <td>{rule.id.toString()}</td>
                <td>{rule.rule_command}</td>
                <td>{rule.adder_user_id.toString()}</td>
                <td>{rule.add_date}</td>
                <td>{rule.deleter_user_id.toString()}</td>
                <td>{rule.delete_date}</td>
            </tr>

        );
    }

};

export default DeletedRuleListItem;