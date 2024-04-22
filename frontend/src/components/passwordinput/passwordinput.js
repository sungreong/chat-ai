import { InputAdornment, withStyles } from '@material-ui/core';
import TextField from '@material-ui/core/TextField';
import { RemoveRedEye } from '@material-ui/icons';
import PropTypes from 'prop-types';
import React, { Component } from 'react';
import styles from './passwordinput.module.css';
import { useState } from 'react';
import VisibilityIcon from '@material-ui/icons/Visibility';
import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';



class PasswordInput extends Component {
    constructor(props) {
      super(props);
  
      this.state = {
        passwordIsMasked: true,
      };
    }
  
    togglePasswordMask = () => {
      this.setState(prevState => ({
        passwordIsMasked: !prevState.passwordIsMasked,
      }));
    };
  
    render() {
      const { classes } = this.props;
      const { passwordIsMasked } = this.state;
  
      return (
        <TextField
          type={passwordIsMasked ? 'password' : 'text'}
          {...this.props}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <RemoveRedEye
                  className={classes.eye}
                  onClick={this.togglePasswordMask}
                />
              </InputAdornment>
            ),
          }}
        />
      );
    }
  }
  
  PasswordInput.propTypes = {
    classes: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired,
    value: PropTypes.string, // 여기를 수정했습니다.
  };
  
const StyledPasswordInput = withStyles(styles)(PasswordInput);

// export default StyledPasswordInput;


const CustomPasswordInput = ({ id, name, placeholder, value, onChange }) => {
  const [passwordVisible, setPasswordVisible] = useState(false);

  const togglePasswordVisibility = () => {
    setPasswordVisible(!passwordVisible);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #ccc', borderRadius: '4px', padding: '5px' }}>
      <input
        id={id}
        type={passwordVisible ? 'text' : 'password'}
        name={name}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        style={{ border: 'none', outline: 'none', flex: 1 }}
        step='any'
      />
      <button
        onClick={togglePasswordVisibility}
        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0' }}
      >
        {passwordVisible ? <VisibilityOffIcon /> : <VisibilityIcon />}
      </button>
    </div>
  );
};

export default CustomPasswordInput;